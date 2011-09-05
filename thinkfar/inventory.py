"""
The inventory is a list of items compiled for some formal purpose.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import TextProperty, StringProperty, IntegerProperty
from google.appengine.ext.db import DateProperty, UserProperty, ReferenceProperty


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

    def buy(self, start_date, price_paid, end_date=None, amount=1, taxes_paid=0, resell_value=None):
        if end_date is None:
            end_date = start_date
        t = InventoryTransaction(
            uid='test', item_set=self,
            start_date=start_date, end_date=end_date, amount=amount,
            from_cash=price_paid, to_taxes=taxes_paid, to_value=resell_value,
        )
        t.put()

    def sell(self, start_date, resell_value, end_date=None, amount=1, taxes_paid=0):
        if end_date is None:
            end_date = start_date
        t = InventoryTransaction(
            uid='test', item_set=self,
            start_date=start_date, end_date=end_date, amount=-amount,
            from_cash=-resell_value, to_taxes=taxes_paid,
        )
        t.put()

    def partial_balance(self, start, end):
        return sum(it.partial_balance(start,end) for it in self.inventory_transactions)
    
    def balance(self, date):
        return sum(it.balance(date) for it in self.inventory_transactions)


class InventoryTransaction(Model):
    """An event in the inventory

    The transaction may have a time extension and in that case it 
    really corresponds to a linear change in the inventory balances.
    
    A transaction that buys a car looks like:

    InventoryTransaction(..., amount=1, from_cash=15000, to_taxes=3500, to_value=10000)
    """
    uid = StringProperty(required=True)
    name = StringProperty()
    description = TextProperty()

    start_date = DateProperty(required=True)
    end_date = DateProperty(required=True)

    item_set = ReferenceProperty(ItemSet, required=True, collection_name='inventory_transactions')
    
    amount = IntegerProperty(required=True)
    from_cash = IntegerProperty(required=True)
    to_taxes = IntegerProperty(required=True)
    to_value = IntegerProperty()

    def partial_balance(self, start, end):
        start_date = self.start_date if (self.start_date > start) else start
        end_date = self.end_date if (self.end_date < end) else end
        delta_days = (end_date - start_date).days
        if delta_days < 0:
            return 0L
        self_delta_days = (self.end_date - self.start_date).days
        if self_delta_days == 0:
            return self.amount
        return self.amount * delta_days // self_delta_days

    def balance(self, date):
        return self.partial_balance(self.start_date, date)


def user_inventory(user, limit=None):
    ItemSet.all().filter('owner =', user).fetch(limit)
