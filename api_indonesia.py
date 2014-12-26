__author__ = 'oonarfiandwi'

from flask import Flask
from flask import request
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from model_profile import Profile
import simplejson as json

"""
this should be data from another API (contact circlecount?)
"""
indonesia_ids = \
    ['107432398539341365940', '107625144935146230047', '106601693943516044496', '104448874055406535418',
     '112354545929966456048', '114384982500350295512', '108286657063314289856', '100376954084559205891',
     '116869234231593219709', '100558479203992663037', '118252948887947024512',
     '102354805749063623353',  # oon arfiandwi
     ]

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')


@app.route('/indonesia', methods=['POST'])
def get_indonesia():
    """
    instance dilingkari.appspot.com will not serve /indonesia to manage quota usage
    """
    if 'dilingkari.appspot.com' in request.url_root:
        return '[]'
    # should response with data from database, direct request to Google+ API is limited (per sec)
    indonesia_users = []
    for profile_id in indonesia_ids:
        # Add the task to the default queue.
        taskqueue.add(url='/p', params={'id': profile_id})
        # request to ndb
        profile = ndb.Key(Profile, profile_id).get()
        if profile is not None:
            user_profile = json.loads(profile.user_data)
            user_dict = {'displayName': user_profile['displayName'], 'id': user_profile['id'],
                         'name': user_profile['name'], 'image': user_profile['image']}
            indonesia_users.append(user_dict)
    return json.dumps(indonesia_users)