__author__ = 'oonarfiandwi'

from google.appengine.ext import ndb


class Profile(ndb.Model):
    """
    Google+ User Profile And Activity
    """
    user_data = ndb.JsonProperty(indexed=False)
    user_lastupdate = ndb.DateTimeProperty(auto_now=False)
    activity_data = ndb.JsonProperty(indexed=False)
    activity_lastupdate = ndb.DateTimeProperty(auto_now=False)
