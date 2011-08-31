"""
The inventory is a list of items compiled for some formal purpose.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import BooleanProperty, FloatProperty, DateProperty
from google.appengine.ext.db import TextProperty, StringProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty


from thinkfar.accounting import Transaction, TransactionEntry


class ItemClass(Model):
	"""
	A broad class of inventory items, i.e. 'a share' or 'a car'

	It defines default behaviour of the item class, its accounts, etc.
	ItemClass'es are shared between all users (for now).
	"""
	uuid = StringProperty(required=True)
	name = StringProperty(required=True)
    description = TextProperty()


class ItemSet(Model):
	"""
	An entry into the invetory, i.e. 'GOOG shares' or 'my Honda Civic'

	It stores data specific to a set of items that can be safely shared
	bitween scenarios, like past size, income and expenses,	and likely 
	furure ones.
	"""
	owner = UserProperty(required=True)

	uid = StringProperty(required=True)
	name = StringProperty(required=True)
	description = TextProperty()

	item_class = ReferenceProperty(ItemClass, required=True)


class InventoryTransactionEntry(TransactionEntry):
	item_set = ReferenceProperty(ItemSet, required=True, collection_name='transactions')


def user_inventory(user, limit=None):
	Item.all().filter('owner =', user).fetch(limit)
