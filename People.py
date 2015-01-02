__author__ = 'oonarfiandwi'

import simplejson as json

"""
    Sample implementation of Class in Python
    https://docs.python.org/2/tutorial/classes.html
"""


class People:
    """
        People is a model from Google+ API People
        https://developers.google.com/+/api/latest/people
    """
    def __init__(self, people_json):
        self.person = json.loads(people_json)
        self.id = self.person.get('id')
        self.name = self.person.get('name')  # object
        self.image = self.person.get('image')  # object
        self.cover = self.person.get('cover')  # object
        self.gender = self.person.get('gender')
        self.aboutMe = self.person.get('aboutMe')
        self.verified = self.person.get('verified')
        self.isPlusUser = self.person.get('isPlusUser')
        self.displayName = self.person.get('displayName')
        self.plusOneCount = self.person.get('plusOneCount')
        self.braggingRights = self.person.get('braggingRights')
    
    def get_image_url(self):
        user_image = self.image
        sz_index = user_image['url'].find('?sz=')
        if sz_index > 0:
            user_image['url'] = user_image['url'][:sz_index] + '?sz=350'  # change image size to 350
        return user_image['url']
    
    def get_image(self):
        user_image = self.image
        sz_index = user_image['url'].find('?sz=')
        if sz_index > 0:
            user_image['url'] = user_image['url'][:sz_index] + '?sz=350'  # change image size to 350
        return user_image
