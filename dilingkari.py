from flask import Flask
from google.appengine.api import urlfetch
import jinja2
import os
import urllib
import simplejson as json

app = Flask(__name__)
app.config['DEBUG'] = True

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


@app.route('/')
@app.route('/index')
def index():
    output_str = '<h1>Hello World!</h1>'
    form_fields = { "nitems": "all", }
    form_data = urllib.urlencode(form_fields)
    result = urlfetch.fetch(url='http://dilingkari.appspot.com/indonesia',
                        payload=form_data,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                        deadline=60)
    users = []
    if result.status_code == 200:
        users = json.loads(result.content)
    template_values = {
        'body_text': output_str,
        'users': users
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