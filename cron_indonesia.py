__author__ = 'oonarfiandwi'

from flask import Flask, request
from google.appengine.api import taskqueue

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/cron_indonesia')
def cron_indonesia():
    """
    instance dilingkari.appspot.com will not serve cron to preserve quota usage
    """
    if not 'dilingkari.appspot.com' in request.url_root:
        taskqueue.add(url='/indonesia', params={'nitems': 'all'}, method="POST")
    return ''