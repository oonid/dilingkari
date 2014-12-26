__author__ = 'oonarfiandwi'

from flask import Flask, request
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache
from google.appengine.ext import ndb
from apiclient import discovery
from datetime import datetime
from model_profile import Profile

import httplib2
import simplejson as json

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')

@app.route('/a', methods=['POST'])
def api_activity():
    """ instance dilingkari.appspot.com will not serve /a to manage quota usage """
    if 'dilingkari.appspot.com' in request.url_root:
        return '{}'
    profile_id = request.form['id']
    http = credentials.authorize(httplib2.Http(memcache))
    service_http = discovery.build("plus", "v1", http=http)
    activities = service_http.activities().list(userId=profile_id, collection='public').execute(http=http)
    updated = activities.get('updated')
    updated_datetime = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S.%fZ')
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
            user_profile.activity_updated = updated_datetime
            user_profile.activity_lastupdate = datetime.now()
        user_profile.put()

    update_profile()
    return activities_json
