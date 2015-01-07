__author__ = 'oonarfiandwi'

from google.appengine.ext import ndb


class Profile(ndb.Model):
    """
    Google+ User Profile And Activity
    """
    user_data = ndb.JsonProperty(indexed=False)
    user_lastupdate = ndb.DateTimeProperty(auto_now=False)
    user_is_verified = ndb.BooleanProperty(indexed=True)
    activity_data = ndb.JsonProperty(indexed=False)
    activity_updated = ndb.DateTimeProperty(auto_now=False, indexed=True)
    activity_lastupdate = ndb.DateTimeProperty(auto_now=False)
