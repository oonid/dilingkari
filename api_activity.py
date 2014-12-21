__author__ = 'oonarfiandwi'

from flask import Flask
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache
from apiclient import discovery
import httplib2
import datetime as dt
import simplejson as json

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')

@app.route('/a/<int:profile_id>')
def get_activity(profile_id):
    http = credentials.authorize(httplib2.Http(memcache))
    service_http = discovery.build("plus", "v1", http=http)
    activities = service_http.activities().list(userId=profile_id, collection='public').execute(http=http)
    #items = activities.get('items', [])
    #text = ''
    #for activity in items:
    #    published = activity['published']
    #    nowdt = dt.datetime.now()
    #    newdt = dt.datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%fZ')
    #    text += str(nowdt-newdt)
    #    text += activity['title']
    #    text += activity['url']
    #    text += '<br/>'
    #return 'get activity for Profile ID: %d <br/> %s' % (profile_id, text)
    return json.dumps(activities)
