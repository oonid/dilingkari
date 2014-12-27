__author__ = 'oonarfiandwi'

from flask import Flask
from flask import request
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from google.appengine.ext.db import stats
from model_profile import Profile
from datetime import datetime, timedelta

import simplejson as json
import re

"""
this should be data from another API (contact circlecount? http://www.circlecount.com/id/profileslist/)
"""
indonesia_ids = \
    ['107432398539341365940', '107625144935146230047', '106601693943516044496', '104448874055406535418',
     '112354545929966456048', '114384982500350295512', '108286657063314289856', '100376954084559205891',
     '116869234231593219709', '100558479203992663037', '118252948887947024512', '113394938579974212693',
     '112638457196220461637', '101810166866201144931', '106939868938222633265', '102822538152349669747',
     '107507070338583266314', '102024051895024187351', '117108236116237500441', '118214294405590069582',
     '105628667513453263078', '113811258740009429740', '104954947323368041426', '118343307903587596704',
     '101778343594604092334', '105924429773397501596', '111156704479775949627', '104879387838839120510',
     '102250841784466654092', '113014617490520808583', '101928252051944612621', '101682734905774807138',
     '104357255131643322237', '102802823311284245007', '105687286181087087938', '106481269342600411633',
     '104689423159256002886',
     '102354805749063623353',  # google.com/+oonarfiandwi
     '108287824657082742169',  # google.com/+eunikekartini
     ]

data_expired_time_in_seconds = 60 * len(indonesia_ids)

app = Flask(__name__)
app.config['DEBUG'] = True
credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/plus.me')


@app.route('/indonesia', methods=['POST'])
def get_indonesia():
    """
    instance dilingkari.appspot.com will not serve /indonesia to preserve quota usage
    """
    if 'dilingkari.appspot.com' in request.url_root:
        return '[]'
    nitems = int(request.form['nitems'])
    page = int(request.form['page'])
    offset = 0
    if page > 0:
        offset = (page-1) * nitems
    # process phase 1 (update database)
    for profile_id in indonesia_ids:
        # request to ndb
        profile = ndb.Key(Profile, profile_id).get()
        if profile is None:
            # Add the task to the default queue.
            taskqueue.add(url='/p', params={'id': profile_id})
            taskqueue.add(url='/a', params={'id': profile_id})
        else:
            # check if the database is expired? update via taskqueue if database expired
            user_lastupdate = profile.user_lastupdate
            if user_lastupdate is None:
                user_lastupdate = datetime.now() - timedelta(seconds=(data_expired_time_in_seconds+1))
            user_delta = datetime.now() - user_lastupdate
            if user_delta.total_seconds() > data_expired_time_in_seconds:
                # Add the task to the default queue after expired
                taskqueue.add(url='/p', params={'id': profile_id})

            # check if the database is expired? update via taskqueue if database expired
            activity_lastupdate = profile.activity_lastupdate
            if activity_lastupdate is None:
                activity_lastupdate = datetime.now() - timedelta(seconds=(data_expired_time_in_seconds+1))
            activity_delta = datetime.now() - activity_lastupdate
            if activity_delta.total_seconds() > data_expired_time_in_seconds:
                # Add the task to the default queue after expired
                taskqueue.add(url='/a', params={'id': profile_id})

    # process phase 2 (response with data from Datastore)
    profiles = Profile.query().order(-Profile.activity_updated).fetch(nitems, offset=offset)
    indonesia_users = []
    for profile in profiles:
        # 'updated' is field from Google+ API activities related to specified user
        activity_updated = profile.activity_updated
        last_activity = '(unknown)'
        if activity_updated is not None:
            last_activity = get_delta(activity_updated)

        # user profile is a return of Google+ API people
        user_profile = json.loads(profile.user_data)
        if user_profile is not None:
            user_image = user_profile['image']
            m = re.search('(.*)\?sz=(\d+)', user_image['url'])
            if m:
                user_image['url'] = m.group(1) + '?sz=350'  # change image size to 350
            user_dict = {'displayName': user_profile['displayName'], 'id': user_profile['id'],
                         'name': user_profile['name'], 'image': user_image,
                         'last_activity': last_activity}
            indonesia_users.append(user_dict)

    return json.dumps(indonesia_users)


@app.route('/count_indonesia', methods=['POST'])
def count_indonesia():
    """
    instance dilingkari.appspot.com will not serve /count_indonesia to preserve quota usage
    """
    if 'dilingkari.appspot.com' in request.url_root:
        return '0'
    nitems = int(request.form['nitems'])
    kind_stats = stats.KindStat().all().filter("kind_name =", "Profile").get()
    return str(kind_stats.count)


def get_delta(updated_datetime):
    text = ''
    delta = datetime.now() - updated_datetime
    total_sec = delta.days*24*60*60+delta.seconds
    total_min, secs = divmod(total_sec, 60)
    total_hrs, mins = divmod(total_min, 60)
    total_days, hours = divmod(total_hrs, 24)
    if total_days > 1:
        text += str(total_days) + ' days '
    elif total_days == 1:
        text += '1 day '
    if hours > 1:
        text += str(hours) + ' hours '
    elif hours == 1:
        text += '1 hour '
    if mins > 1:
        text += str(mins) + ' minutes '
    elif mins == 1:
        text += '1 minute '
    #if secs > 1:
    #    text += str(secs) + ' seconds '
    #elif secs == 1:
    #    text += '1 second '
    text += 'ago.'
    return text