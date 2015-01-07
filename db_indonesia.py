__author__ = 'oonarfiandwi'

from flask import Flask
from flask import request
from google.appengine.api import taskqueue, memcache
from google.appengine.datastore import entity_pb
from google.appengine.ext import ndb
from model_profile import Profile
from datetime import datetime, timedelta
from os import environ
from logging import error
from People import People

import simplejson as json

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
     '104689423159256002886', '112498833559117226731', '117295569606047532013', '103537465357175776468',
     '115597363814522022890', '107320220329059497679', '105178080302702831809', '100774395895038903027',
     '112705926429019733037', '100402345470048010212', '114805887372864153486', '116709755762272494241',
     '108616701717565220964', '110136850451233606756', '111583929679906329750', '104898639851403166441',
     '111127624692119872997', '108373180619624143682', '102998236025601701615', '105965978920361943349',
     '105195268799430749865', '115973691986694822274', '107081533430574750743', '113256479008912400953',
     '104801716294445103557', '105088313441807388577', '101384003234517231964', '100064238664911237662',
     '109462018029692971187', '110315331954590884708', '100401573219575028576', '100644820619132604408',
     '105712719816201451857', '110999762221836400675', '110812640907879540139', '105228323457033543279',
     '101659112905585086771', '115238169369932529641', '108459444669704402860', '112376808056265675751',
     '113062200675898364899', '113790517052179637060', '117913114635691687230', '113609819507715309506',
     '103880880568089001619', '115230166193627948492', '109292455464540990594', '102748241426689710933',
     '103694044190443947860', '109499153411718537835', '117428153251899145718', '116564404830129709349',
     '114673087345260135832', '110164135613724623208', '118003926024310980798', '106722816607940762364',
     '109128804280051726481', '117823130965889718161', '103822648474011295451', '102875388305901271896',
     '116430720068309201654', '111774305345889696894', '106323274296699264295', '116418544068626962508',
     '101249952574241217402', '116729759094961531076', '102979881173826058281', '105371406280194453518',
     '101898587084201015993', '116610801738829783940', '105887489575344254572', '108831587043640764362',
     '105810954071112361976', '103105202350431983844', '101981660178179618739', '101701920696045165687',
     '112669538420258358861', '100100066894130591020', '113353870864715471985', '100353356311983330157',
     '117762593332079535969', '107507539268974734333', '104707033302283722890', '111115958534146764360',
     '107903295674078716857', '105154411599585458501', '111034269652878471427', '100816763676617074031',
     '113906325992504847601', '116282402565362776252', '114210320721253434841', '116653828204029811729',
     '115041340633616548475', '112878166140838268180', '116540026763084000945', '113576769754615264600',
     '105751407373154489199',  # google.com/+AryanataRazki
     '106180130032686806318',  # google.com/+intananggita
     '103164032603442685281',  # tikabanget
     '102354805749063623353',  # google.com/+oonarfiandwi
     '108287824657082742169',  # google.com/+eunikekartini
     # verified users
     '112630572986759127431', '107473738764732280406', '113731426897634311366',
     # not-active-user
     '101874797485064592775', '103112988688147257701', '100575364581092867206', '111000770457789664008',
     '108904522549191242618', '108288059417021620647', '100652824519298040016', '102185792362815488008',
     ]

profile_expired_time_in_seconds = 60 * len(indonesia_ids)
activity_expired_time_in_seconds = 1800

"""
TaskQueue only support relative URL
"""
TQ_URL_PROFILE = '/p'
TQ_URL_ACTIVITY = '/a'


app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/indonesia', methods=['POST'])
def get_indonesia():
    """ only DB_INSTANCE serve /indonesia to preserve quota usage """
    if not environ['DB_INSTANCE'] in request.url_root:
        return '[]'
    nitems = int(request.form['nitems'])
    page = int(request.form['page'])
    offset = 0
    if page > 0:
        offset = (page-1) * nitems

    # process phase 1 (update database)
    # now handled by cron per 10 minutes

    # process phase 2 (response with data from memcache or Datastore)
    # unfortunately total data from Datastore is bigger than max allowed on memcache (1MB)
    # so we will split the query, and optimized with the current profile on memcache
    profiles = deserialize_entities(memcache.get('profile_by_activity_updated:%d:%d' % (nitems, offset)))
    if profiles is None:
        profiles = Profile.query().order(-Profile.activity_updated). \
            fetch(nitems, offset=offset, projection=[Profile.activity_updated])
        if not memcache.add('profile_by_activity_updated:%d:%d' % (nitems, offset), serialize_entities(profiles), 60):
            error('Memcache set failed: profile_by_activity_updated:%d:%d' % (nitems, offset))

    indonesia_users = []
    for profile in profiles:
        # get data from memcache or datastore for specific user
        p = get_profile(profile.key.id())
        
        # 'updated' is field from Google+ API activities related to specified user
        last_activity = '(unknown)'
        activity_updated = profile.activity_updated
        if activity_updated is not None:
            last_activity = get_delta(activity_updated)
            if p.activity_data is not None:
                activity_data = json.loads(p.activity_data)
                items = activity_data['items']
                #items = activity_data.get('items', [])
                if len(items) > 0:
                    item_object = items[0]['object']
                    t_reshare = str(item_object['resharers']['totalItems'])
                    t_plusone = str(item_object['plusoners']['totalItems'])
                    t_comment = str(item_object['replies']['totalItems'])
                    last_activity += '<br/>('+t_reshare+' reshares, '+t_plusone+' <b>+1</b>, '+t_comment+' comments)'

        # user profile is a return of Google+ API people
        person = People(p.user_data)
        if person is not None:
            user_dict = {'displayName': person.displayName, 'id': person.id,
                         'name': person.name, 'image': person.get_image(), 'verified': person.verified,
                         'last_activity': last_activity}
            indonesia_users.append(user_dict)

    data_indonesia_users = {'total_data': count_indonesia(), 'paging_data': indonesia_users}
    return json.dumps(data_indonesia_users)


@app.route('/verified_indonesia', methods=['POST'])
def get_verified():
    """ only DB_INSTANCE serve /verified to preserve quota usage """
    if not environ['DB_INSTANCE'] in request.url_root:
        return '[]'
    nitems = int(request.form['nitems'])
    page = int(request.form['page'])
    offset = 0
    if page > 0:
        offset = (page-1) * nitems

    # process phase 2 (response with data from memcache or Datastore)
    # unfortunately total data from Datastore is bigger than max allowed on memcache (1MB)
    # so we will split the query, and optimized with the current profile on memcache
    profiles = deserialize_entities(memcache.get('profile_verified:%d:%d' % (nitems, offset)))
    if profiles is None:
        profiles = Profile.query(Profile.user_is_verified == True).order(-Profile.activity_updated). \
            fetch(nitems, offset=offset, projection=[Profile.activity_updated])
        if not memcache.add('profile_verified:%d:%d' % (nitems, offset), serialize_entities(profiles), 60):
            error('Memcache set failed: profile_verified:%d:%d' % (nitems, offset))

    verified_users = []
    for profile in profiles:
        # get data from memcache or datastore for specific user
        p = get_profile(profile.key.id())

        # 'updated' is field from Google+ API activities related to specified user
        last_activity = '(unknown)'
        activity_updated = profile.activity_updated
        if activity_updated is not None:
            last_activity = get_delta(activity_updated)
            if p.activity_data is not None:
                activity_data = json.loads(p.activity_data)
                items = activity_data['items']
                #items = activity_data.get('items', [])
                if len(items) > 0:
                    item_object = items[0]['object']
                    t_reshare = str(item_object['resharers']['totalItems'])
                    t_plusone = str(item_object['plusoners']['totalItems'])
                    t_comment = str(item_object['replies']['totalItems'])
                    last_activity += '<br/>('+t_reshare+' reshares, '+t_plusone+' <b>+1</b>, '+t_comment+' comments)'

        # user profile is a return of Google+ API people
        person = People(p.user_data)
        if person is not None:
            user_dict = {'displayName': person.displayName, 'id': person.id,
                         'name': person.name, 'image': person.get_image(), 'verified': person.verified,
                         'last_activity': last_activity}
            verified_users.append(user_dict)

    data_verified_users = {'total_data': count_verified(), 'paging_data': verified_users}
    return json.dumps(data_verified_users)


def count_verified():
    count = memcache.get('count_verified')
    if count is not None:
        return count
    else:
        count = Profile.query(Profile.user_is_verified == True).count(limit=None, keys_only=True)
        if not memcache.add('count_verified', count, 600):  # 600 seconds
            error('Memcache set failed: count_verified')
        return count


def count_indonesia():
    count = memcache.get('count_indonesia')
    if count is not None:
        return count
    else:
        count = Profile.query().count(limit=None, keys_only=True)
        if not memcache.add('count_indonesia', count, 600):  # 600 seconds
            error('Memcache set failed: count_indonesia')
        return count


def get_profile(profile_id):
    profile = deserialize_entities(memcache.get('profile:%s' % profile_id))
    if profile is None:
        profile = ndb.Key(Profile, profile_id).get()
        if profile is not None:  # None in memcache, but not None on datastore
            if not memcache.add('profile:%s' % profile_id, serialize_entities(profile), 600):  # 600 seconds
                error('Memcache set failed: profile:%s' % profile_id)

    return profile


@app.route('/update_db_indonesia', methods=['POST'])
def update_db_indonesia():
    """ only DB_INSTANCE serve /update_db_indonesia to preserve quota usage """
    if environ['DB_INSTANCE'] in request.url_root:
        nitems = int(request.form['nitems'])
        page = int(request.form['page'])

        # process phase 1 (update database)
        for profile_id in indonesia_ids:
            # request to memcache and ndb
            profile = deserialize_entities(memcache.get('profile:%s' % profile_id))
            if profile is None:
                profile = ndb.Key(Profile, profile_id).get()
                if profile is not None:  # None in memcache, but not None on datastore
                    if not memcache.add('profile:%s' % profile_id, serialize_entities(profile), 600):  # 600 seconds
                        error('Memcache set failed: profile:%s' % profile_id)

            if profile is None:  # None in Datastore
                # Add the task to the default queue.
                taskqueue.add(url=TQ_URL_PROFILE, params={'id': profile_id})
                taskqueue.add(url=TQ_URL_ACTIVITY, params={'id': profile_id})
            else:
                # check if the database is expired? update via taskqueue if database expired
                user_lastupdate = profile.user_lastupdate
                if user_lastupdate is None:
                    user_lastupdate = datetime.now() - timedelta(seconds=(profile_expired_time_in_seconds+1))
                user_delta = datetime.now() - user_lastupdate
                if user_delta.total_seconds() > profile_expired_time_in_seconds:
                    # Add the task to the default queue after expired
                    taskqueue.add(url=TQ_URL_PROFILE, params={'id': profile_id})

                # check if the database is expired? update via taskqueue if database expired
                activity_lastupdate = profile.activity_lastupdate
                if activity_lastupdate is None:
                    activity_lastupdate = datetime.now() - timedelta(seconds=(activity_expired_time_in_seconds+1))
                activity_delta = datetime.now() - activity_lastupdate
                if activity_delta.total_seconds() > activity_expired_time_in_seconds:
                    # Add the task to the default queue after expired
                    taskqueue.add(url=TQ_URL_ACTIVITY, params={'id': profile_id})

    return '[]'


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


"""
    serialization method
        from blog http://blog.notdot.net/2009/9/Efficient-model-memcaching
    updated from db to ndb using method 
        from blog http://www.dylanv.org/2012/08/22/a-hitchhikers-guide-to-upgrading-app-engine-models-to-ndb/
"""


def serialize_entities(models):
    if models is None:
        return None
    elif isinstance(models, ndb.Model):
        # Just one instance
        return ndb.ModelAdapter().entity_to_pb(models).Encode()
    else:
        # A list
        return [ndb.ModelAdapter().entity_to_pb(x).Encode() for x in models]


def deserialize_entities(data):
    # precondition: model class must be imported
    if data is None:
        return None
    elif isinstance(data, str):
        # Just one instance
        return ndb.ModelAdapter().pb_to_entity(entity_pb.EntityProto(data))
    else:
        return [ndb.ModelAdapter().pb_to_entity(entity_pb.EntityProto(x)) for x in data]
