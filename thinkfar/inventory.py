"""
The inventory is a list of items compiled for some formal purpose.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import TextProperty, StringProperty, IntegerProperty
from google.appengine.ext.db import DateProperty, UserProperty, ReferenceProperty


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


class Currency(Model):
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()


class User(Model):
    uid = StringProperty(required=True)
    name = StringProperty()

    principal = UserProperty(required=True)


class AccountingUniverse(Model):
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()


class Book(Model):
    uid = StringProperty(required=True)
    name = StringProperty()
    description = TextProperty()

    owner = ReferenceProperty(User, required=True, collection_name='books')
    accounting_universe = ReferenceProperty(AccountingUniverse, required=True)
    currency = ReferenceProperty(Currency, required=True)


class ItemClass(Model):
    """
    A broad class of inventory items, i.e. 'a share' or 'a car'

    It defines default behavior of the item class, its accounts, etc.
    ItemClass'es are shared between all users (for now).
    """
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()

    accounting_universe = ReferenceProperty(AccountingUniverse, collection_name='item_classes')

    def create_itemset(self, book, uid, name, description=None):
        return ItemSet(book=book, item_class=self, uid=uid, name=name, description=description)


class ItemSet(Model):
    """
    An entry into the inventory, i.e. 'GOOG shares' or 'my Honda Civic'

    It stores data specific to a set of items that can be safely shared
    between scenarios, like past size, income and expenses,	and likely 
    future ones.
    """
    book = ReferenceProperty(Book, required=True, collection_name='inventory')
    item_class = ReferenceProperty(ItemClass, required=True)

    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()

    def acquire(self, start_date, end_date=None, amount=1):
    	if end_date is None:
            end_date = start_date
        tx = InventoryTransaction(
            uid='test', item_set=self, amount=amount,
            start_date=start_date, end_date=end_date,
        )
        tx.put()

    def dismiss(self, start_date, end_date=None, amount=1):
        if end_date is None:
            end_date = start_date
        tx = InventoryTransaction(
            uid='test', item_set=self, amount=-amount,
            start_date=start_date, end_date=end_date,
        )
        tx.put()

    def partial_balance(self, start, end):
        return sum(it.partial_balance(start,end) for it in self.inventory_transactions)
    
    def balance(self, date):
        return sum(it.balance(date) for it in self.inventory_transactions)

    def buy(self, start_date, gross_price_paid, amount=1, taxes_paid=0, fees_paid=0, resell_value=None, end_date=None):
        if end_date is None:
            end_date = start_date
        for template in self.item_class.transaction_templates:
            if template.template_type == 'buy':
                pass
        else:
            raise TypeError


class InventoryTransaction(Model):
    """An event in the inventory

    The transaction may have a time extension and in that case it 
    really corresponds to a linear change in the inventory balances.
    """
    uid = StringProperty(required=True)
    name = StringProperty()
    description = TextProperty()

    start_date = DateProperty(required=True)
    end_date = DateProperty(required=True)

    item_set = ReferenceProperty(ItemSet, required=True, collection_name='inventory_transactions')

    amount = IntegerProperty(required=True)

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
