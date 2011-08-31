"""
The inventory is a list of items compiled for some formal purpose.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import BooleanProperty, FloatProperty, DateProperty
from google.appengine.ext.db import TextProperty, StringProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty


class ItemModel(Model):
	name = StringProperty()

class Item(Model):
	owner = UserProperty(required=True)
	item_model = ReferenceProperty(ItemModel, required=True)

	name = StringProperty(required=True)
	description = TextProperty()
	identity = StringProperty()

def user_inventory(user, limit=None):
	Item.all().filter('owner =', user).fetch(limit)
