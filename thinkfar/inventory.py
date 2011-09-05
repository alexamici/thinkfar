"""
The inventory is a list of items compiled for some formal purpose.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import TextProperty, StringProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


class User(Model):
    uid = StringProperty(required=True)
    principal = UserProperty(required=True)

    def setattrs(self, **kwds):
        for key, value in kwds.items():
            setattr(self, key, value)


class ItemClass(Model):
    """
    A broad class of inventory items, i.e. 'a share' or 'a car'

    It defines default behavior of the item class, its accounts, etc.
    ItemClass'es are shared between all users (for now).
    """
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()


class ItemSet(Model):
    """
    An entry into the inventory, i.e. 'GOOG shares' or 'my Honda Civic'

    It stores data specific to a set of items that can be safely shared
    between scenarios, like past size, income and expenses,	and likely 
    future ones.
    """
    owner = ReferenceProperty(User, required=True)

    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()

    def partial_balance(self, start, end):
        return sum(it.partial_balance(start,end) for it in self.inventory_transaction_entries)
    
    def balance(self, date):
        return sum(it.balance(date) for it in self.inventory_transaction_entries)


def user_inventory(user, limit=None):
    ItemSet.all().filter('owner =', user).fetch(limit)
