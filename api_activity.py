__author__ = 'oonarfiandwi'

from flask import Flask, request
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache, urlfetch
from google.appengine.ext import ndb
from apiclient import discovery
from datetime import datetime
from model_profile import Profile

import httplib2
import simplejson as json
import os

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')

"""
you should consider to deploy this to other project (instance),
change this URL to your own project URL
API_INSTANCE environment variable defined at app.yaml
"""
API_ACTIVITY = 'http://' + os.environ['API_INSTANCE'] + '/a/'


@app.route('/a', methods=['POST'])
def api_activity():
    """ only API_INSTANCE serve /a to manage quota usage """
    if os.environ['API_INSTANCE'] in request.url_root:
        profile_id = request.form['id']
        result = urlfetch.fetch(url=API_ACTIVITY+profile_id, method=urlfetch.GET, deadline=60)
        if result.status_code == 200:
            return result.content

    # else (not API_INSTANCE)
    return '{}'


@app.route('/a/<profile_id>')
def get_activity(profile_id):
    """ only API_INSTANCE that will be serve /a/.* """
    if os.environ['API_INSTANCE'] in request.url_root:
        http = credentials.authorize(httplib2.Http(memcache))
        service_http = discovery.build("plus", "v1", http=http)
        activities = service_http.activities().list(userId=profile_id, collection='public').execute(http=http)
        updated = activities.get('updated')
        activities_json = json.dumps(activities)

        key = ndb.Key(Profile, profile_id)
        @ndb.transactional
        def update_profile():
            user_profile = key.get()
            if user_profile is None:
                user_profile = Profile(key=key, activity_data=activities_json, activity_updated=updated_datetime,
                                   activity_lastupdate=datetime.now())
            else:
                user_profile.activity_data = activities_json
                user_profile.activity_lastupdate = datetime.now()
                if updated is not None:
                    user_profile.activity_updated = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S.%fZ')
            user_profile.put()

        update_profile()
        return activities_json

    # else (not API_INSTANCE)
    return '{}'