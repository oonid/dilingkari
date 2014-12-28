__author__ = 'oonarfiandwi'

from flask import Flask, request
from google.appengine.api import urlfetch

import jinja2
import urllib
import simplejson as json
import os

app = Flask(__name__)
app.config['DEBUG'] = True

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

"""
you should consider to deploy this to other project (instance),
change this URL to your own project URL
DB_INSTANCE environment variable defined at app.yaml
"""
API_INDONESIA = 'http://' + os.environ['DB_INSTANCE'] + '/indonesia'
COUNT_INDONESIA = 'http://' + os.environ['DB_INSTANCE'] + '/count_indonesia'


@app.route('/')
@app.route('/index')
def index():
    nitems = '21'
    page = request.args.get('p', '1')
    output_str = 'yang aktif di Google+'
    form_fields = {'nitems': nitems, 'page': page}
    form_data = urllib.urlencode(form_fields)
    result_count_indonesia = urlfetch.fetch(url=COUNT_INDONESIA, payload=form_data, method=urlfetch.POST,
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'}, deadline=60)
    count_indonesia = long(result_count_indonesia.content)
    count = 1
    if count_indonesia > long(nitems):
        count = 1 + int(count_indonesia / long(nitems))
    form_fields = {'nitems': nitems, 'page': page}
    form_data = urllib.urlencode(form_fields)
    result = urlfetch.fetch(url=API_INDONESIA, payload=form_data, method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'}, deadline=60)
    users = []
    if result.status_code == 200:
        users = json.loads(result.content)
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