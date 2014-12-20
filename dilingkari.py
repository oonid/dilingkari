from flask import Flask

import jinja2
import os

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
    gplus_ids = ['116709755762272494241', '102354805749063623353']
    for gplus_id in gplus_ids:
        output_str += gplus_id + '<br/>'
    template_values = {
        'body_text': output_str,
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