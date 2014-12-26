__author__ = 'oonarfiandwi'

from flask import Flask
from flask import request
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache
from google.appengine.ext import ndb
from apiclient import discovery
from model_profile import Profile

import httplib2
import simplejson as json

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')


@app.route('/p/<int:profile_id>')
def get_profile(profile_id):
    http = credentials.authorize(httplib2.Http(memcache))
    service_http = discovery.build("plus", "v1", http=http)
    user = service_http.people().get(userId=profile_id).execute(http=http)
    return json.dumps(user)


@app.route('/p', methods=['POST'])
def api_profile():
    """ instance dilingkari.appspot.com will not serve /p to manage quota usage """
    if 'dilingkari.appspot.com' in request.url_root:
        return '{}'
    profile_id = request.form['id']
    http = credentials.authorize(httplib2.Http(memcache))
    service_http = discovery.build("plus", "v1", http=http)
    user = service_http.people().get(userId=profile_id).execute(http=http)
    user_json = json.dumps(user)

    key = ndb.Key(Profile, profile_id)
    @ndb.transactional
    def update_profile():
        user_profile = key.get()
        if user_profile is None:
            user_profile = Profile(key=key, user_data=user_json)
        else:
            user_profile.user_data = user_json
        user_profile.put()

    update_profile()
    return user_json