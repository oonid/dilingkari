__author__ = 'oonarfiandwi'

from flask import Flask
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache
from apiclient import discovery
import httplib2

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')


@app.route('/p/<int:profile_id>')
def get_profile(profile_id):
    http = credentials.authorize(httplib2.Http(memcache))
    service_http = discovery.build("plus", "v1", http=http)
    user = service_http.people().get(userId=profile_id).execute(http=http)
    text = '<br/>'.join(user)
    return 'get profile for Profile ID: %d <br/> %s' % (profile_id, text)