__author__ = 'oonarfiandwi'

from flask import Flask, request
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache, urlfetch
from google.appengine.ext import ndb
from apiclient import discovery
from model_profile import Profile
from datetime import datetime, timedelta
from People import People

import httplib2
import simplejson as json
import os
import logging

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')

delay_for_users_after_days = 100


"""
you should consider to deploy this to other project (instance),
change this URL to your own project URL
API_INSTANCE environment variable defined at app.yaml
"""
API_PROFILE = 'http://' + os.environ['API_INSTANCE'] + '/p/'


@app.route('/p', methods=['POST'])
def api_profile():
    """
        only DB_INSTANCE serve /p to manage quota usage
        /p is relative URL that hit by db_indonesia
    """
    if os.environ['DB_INSTANCE'] in request.url_root:
        profile_id = request.form['id']
        result = urlfetch.fetch(url=API_PROFILE+profile_id, method=urlfetch.GET, deadline=60)
        if result.status_code == 200:
            user_json = result.content
            if user_json != '{}':
                key = ndb.Key(Profile, profile_id)
                @ndb.transactional
                def update_profile():
                    user_profile = key.get()
                    if user_profile is None:
                        user_profile = Profile(key=key, user_data=user_json, user_lastupdate=datetime.now())
                    else:
                        user_profile.user_data = user_json
                        user_profile.user_lastupdate = datetime.now()
                        activity_updated = user_profile.activity_updated
                        if activity_updated is not None:
                            if datetime.now() - activity_updated > timedelta(days=delay_for_users_after_days):
                                # delay next schedule of in-active user to next 1 day
                                user_profile.user_lastupdate = datetime.now() + timedelta(days=1)
                    
                    # read content from Google+ API People
                    person = People(user_json)
                    user_profile.user_is_verified = person.verified

                    user_profile.put()

                update_profile()

            return user_json

    # else (not DB_INSTANCE)
    return '{}'


@app.route('/p/<profile_id>')
def get_profile(profile_id):
    """ only API_INSTANCE that will be serve /p/.* """
    if os.environ['API_INSTANCE'] in request.url_root:
        http = credentials.authorize(httplib2.Http(memcache))
        service_http = discovery.build("plus", "v1", http=http)
        user = service_http.people().get(userId=profile_id).execute(http=http)

        return json.dumps(user)
    
    # else (not API_INSTANCE)
    return '{}'