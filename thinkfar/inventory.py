"""
The inventory is a list of items compiled for some formal purpose.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import TextProperty, StringProperty, IntegerProperty
from google.appengine.ext.db import DateProperty, UserProperty, ReferenceProperty


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.8-alpha'


class Currency(Model):
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()


class User(Model):
    uid = StringProperty(required=True, validator=lambda x: x[5])
    name = StringProperty()

    principal = UserProperty(required=True)


class AccountingUniverse(Model):
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()


class Book(Model):
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()

    owner = ReferenceProperty(User, required=True, collection_name='books')
    accounting_universe = ReferenceProperty(AccountingUniverse, required=True)
    currency = ReferenceProperty(Currency, required=True)
    default_cash_account = ReferenceProperty(collection_name='default_cash_account_of')
    default_equity_account = ReferenceProperty(collection_name='default_equity_account_of')

    user_books_limit = 10

    def __init__(self, *args, **keys):
        try:
            if keys['owner'].books.count() >= self.user_books_limit:
                raise ValueError('user_books_limit exceeded')
        except (KeyError, AttributeError):
            pass
        super(Book, self).__init__(*args, **keys)


class ItemSet(Model):
    """
    An entry into the inventory, i.e. 'GOOG shares' or 'my Honda Civic'

    It stores data specific to a set of items that can be safely shared
    between scenarios, like past size, income and expenses,	and likely 
    future ones.
    """
    book = ReferenceProperty(Book, required=True, collection_name='inventory')
    # the intended reference_class is thinkfar.accounting.ItemClass
    item_class = ReferenceProperty()

    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()

    def acquire(self, start_date, uid=None, end_date=None, amount=1, **kargs):
    	if end_date is None:
            end_date = start_date
        if uid is None:
            uid = start_date.isoformat()
        itx = InventoryTransaction(
            uid=uid, item_set=self, amount=amount,
            start_date=start_date, end_date=end_date,
            **kargs
        )
        itx.put()
        return itx

    def dismiss(self, start_date, uid=None, end_date=None, amount=1, **kargs):
        if end_date is None:
            end_date = start_date
        if uid is None:
            uid = start_date.isoformat()
        itx = InventoryTransaction(
            uid=uid, item_set=self, amount=-amount,
            start_date=start_date, end_date=end_date,
            **kargs
        )
        itx.put()
        return itx

    def partial_balance(self, start, end):
        return sum(it.partial_balance(start,end) for it in self.inventory_transactions)
    
    def balance(self, date):
        return sum(it.balance(date) for it in self.inventory_transactions)


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
