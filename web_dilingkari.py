__author__ = 'oonarfiandwi'

from flask import Flask, request
from google.appengine.api import urlfetch, memcache
from os import path, environ

import jinja2
import urllib
import simplejson as json
import logging

app = Flask(__name__)
app.config['DEBUG'] = True

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(path.join(path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

"""
you should consider to deploy this to other project (instance),
change this URL to your own project URL
DB_INSTANCE environment variable defined at app.yaml
beware that WEB_INSTANCE is multiple domain name
"""
DB_PROFILE = 'http://' + environ['DB_INSTANCE'] + '/profile'
DB_INDONESIA = 'http://' + environ['DB_INSTANCE'] + '/indonesia'
DB_VERIFIED_INDONESIA = 'http://' + environ['DB_INSTANCE'] + '/verified_indonesia'
UPDATE_DB_INDONESIA = 'http://' + environ['DB_INSTANCE'] + '/update_db_indonesia'


@app.route('/')
@app.route('/index')
def index():
    nitems = '21'
    page = request.args.get('p', '1')
    output_str = 'yang aktif di Google+'
    
    form_fields = {'nitems': nitems, 'page': page}
    form_data = urllib.urlencode(form_fields)

    users_data = {}
    # try to load data from memcache
    users_json = memcache.get('users_content:%s:%s' % (nitems, page))
    if users_json is None:
        result = urlfetch.fetch(url=DB_INDONESIA, payload=form_data, method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}, deadline=60)
        if result.status_code == 200:
            users_data = json.loads(result.content)
            if not memcache.add('users_content:%s:%s' % (nitems, page), result.content, 300):  # 300 seconds
                logging.error('Memcache set failed: users_content:%s:%s' % (nitems, page))
    else:
        users_data = json.loads(users_json)

    count_indonesia = long(users_data['total_data'])
    count = 1
    if count_indonesia > long(nitems):
        count = 1 + int(count_indonesia / long(nitems))

    users = users_data['paging_data']

    template_values = {
        'body_text': output_str,
        'users': users,
        'page': int(page),
        'last_page': count,
        'base_url': request.base_url
    }
    template = JINJA_ENVIRONMENT.get_template('index.html')
    return template.render(template_values)


@app.route('/profile/<profile_id>')
def profile(profile_id):
    form_fields = {'id': profile_id}
    form_data = urllib.urlencode(form_fields)
    result = urlfetch.fetch(url=DB_PROFILE, payload=form_data, method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'}, deadline=60)
    activity_data = ''
    if result.status_code == 200:
        activity_data = result.content

    template_values = {
        'id': profile_id,
        'body_text': '',
        'base_url': request.base_url
    }
    template = JINJA_ENVIRONMENT.get_template('profile.html')
    return template.render(template_values)


@app.route('/verified')
def verified():
    nitems = '21'
    page = request.args.get('p', '1')
    output_str = 'yang terverifikasi di Google+'

    form_fields = {'nitems': nitems, 'page': page}
    form_data = urllib.urlencode(form_fields)

    users_data = {}
    # try to load data from memcache
    users_json = memcache.get('verified_content:%s:%s' % (nitems, page))
    if users_json is None:
        result = urlfetch.fetch(url=DB_VERIFIED_INDONESIA, payload=form_data, method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}, deadline=60)
        if result.status_code == 200:
            users_data = json.loads(result.content)
            if not memcache.add('verified_content:%s:%s' % (nitems, page), result.content, 300):  # 300 seconds
                logging.error('Memcache set failed: verified_content:%s:%s' % (nitems, page))
    else:
        users_data = json.loads(users_json)

    count_verified = long(users_data['total_data'])
    count = 1
    if count_verified > long(nitems):
        count = 1 + int(count_verified / long(nitems))

    users = users_data['paging_data']

    template_values = {
        'body_text': output_str,
        'users': users,
        'page': int(page),
        'last_page': count,
        'base_url': request.base_url
    }
    template = JINJA_ENVIRONMENT.get_template('index.html')
    return template.render(template_values)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL. (' + str(e) + ')', 404


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
#if __name__ == '__main__':
#     app.run()