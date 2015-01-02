__author__ = 'oonarfiandwi'

from flask import Flask, request
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache, urlfetch
from google.appengine.ext import ndb
from apiclient import discovery
from datetime import datetime, timedelta
from model_profile import Profile

import httplib2
import simplejson as json
import os

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')

delay_for_users_after_days = 100

"""
you should consider to deploy this to other project (instance),
change this URL to your own project URL
API_INSTANCE environment variable defined at app.yaml
"""
API_ACTIVITY = 'http://' + os.environ['API_INSTANCE'] + '/a/'


@app.route('/a', methods=['POST'])
def api_activity():
    """
        only DB_INSTANCE serve /a to manage quota usage
        /a is relative URL that hit by db_indonesia
    """
    if os.environ['DB_INSTANCE'] in request.url_root:
        profile_id = request.form['id']
        result = urlfetch.fetch(url=API_ACTIVITY+profile_id, method=urlfetch.GET, deadline=60)
        if result.status_code == 200:
            activities_json = result.content
            if activities_json != '{}':
                activities = json.loads(activities_json)
                updated = activities.get('updated')
                
                key = ndb.Key(Profile, profile_id)
                @ndb.transactional
                def update_profile():
                    user_profile = key.get()
                    if user_profile is None:
                        user_profile = Profile(key=key, activity_data=activities_json,
                                               activity_lastupdate=datetime.now())
                    else:
                        user_profile.activity_data = activities_json
                        user_profile.activity_lastupdate = datetime.now()

                    if updated is not None:
                        updated_datetime = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S.%fZ')
                        user_profile.activity_updated = updated_datetime
                        if datetime.now() - updated_datetime > timedelta(days=delay_for_users_after_days):
                            # delay next schedule of in-active user to next 1 day
                            user_profile.activity_lastupdate = datetime.now() + timedelta(days=1)
                    else:  # updated data from API is None
                        # delay next schedule of in-active user to next 1 day
                        user_profile.activity_lastupdate = datetime.now() + timedelta(days=1)

                    user_profile.put()

                update_profile()

            return activities_json

    # else (not DB_INSTANCE)
    return '{}'


@app.route('/a/<profile_id>')
def get_activity(profile_id):
    """ only API_INSTANCE that will be serve /a/.* """
    if os.environ['API_INSTANCE'] in request.url_root:
        http = credentials.authorize(httplib2.Http(memcache))
        service_http = discovery.build("plus", "v1", http=http)
        activities = service_http.activities().list(userId=profile_id, collection='public').execute(http=http)

        return json.dumps(activities)

    # else (not API_INSTANCE)
    return '{}'