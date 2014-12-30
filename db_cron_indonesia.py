__author__ = 'oonarfiandwi'

from flask import Flask, request
from google.appengine.api import taskqueue

import os

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/cron_indonesia')
def cron_indonesia():
    """ only DB_INSTANCE serve cron to preserve quota usage """
    if os.environ['DB_INSTANCE'] in request.url_root:
        taskqueue.add(url='/update_db_indonesia', params={'nitems': '1', 'page': '1'}, method="POST")
    return ''