__author__ = 'oonarfiandwi'

from flask import Flask, request
from os import environ
from google.appengine.ext import ndb
from model_profile import Profile

import simplejson as json


app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/profile', methods=['POST'])
def get_profile():
    """ only DB_INSTANCE that will be serve /profile """
    if environ['DB_INSTANCE'] in request.url_root:
        profile_id = request.form['id']
        profile = ndb.Key(Profile, profile_id).get()
        if profile is not None:
            activity_data = json.loads(profile.activity_data)
            items = activity_data.get('items', [])
            item = items[0]
            return json.dumps(item)
    
    # else (not DB_INSTANCE)
    return ''