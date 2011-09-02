"""
'Price is what you pay. Value is what you get.' Warren Buffett, 2008.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import BooleanProperty, IntegerProperty, DateProperty
from google.appengine.ext.db import TextProperty, StringProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty
from google.appengine.ext.db.polymodel import PolyModel

from thinkfar.inventory import ItemSet


class GenericAccount(PolyModel):
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()

    def setattrs(self, **kwds):
        for key, value in kwds.items():
            setattr(self, key, value)


class AccountingTreeRoot(GenericAccount):
    pass

class TotalAccount(GenericAccount):
    is_asset = BooleanProperty(default=False)
    is_liability = BooleanProperty(default=False)
    is_revenue = BooleanProperty(default=False)
    is_expense = BooleanProperty(default=False)

    parent_account = ReferenceProperty(AccountingTreeRoot, collection_name='total_accounts')

    @property
    def is_balance_sheet(self):
        return self.is_asset or self.is_liability

class AggregateAccount(GenericAccount):
    """
    Abstract definition of an aggregate accounts

    Accounts trees are global and shared between all users.
    Only a root account has no parent_account and scenarios
    should point to a root account.
    """
    parent_account = ReferenceProperty(TotalAccount, collection_name='aggregate_accounts')

class Account(GenericAccount):
    parent_account = ReferenceProperty(AggregateAccount, collection_name='accounts')


class Scenario(Model):
    owner = UserProperty(required=True)

    name = StringProperty(required=True, default=u'Default Portfolio')
    description = TextProperty()

    start_date = DateProperty(required=True)


class Transaction(Model):
    """An event in the double-entry book

    The transaction may have a time extension and in that case it 
    really corresponds to a linear change in the account balances.
    """
    uid = StringProperty(required=True)
    name = StringProperty()
    description = TextProperty()

    start_date = DateProperty(required=True)
    end_date = DateProperty(required=True)

    scenario = ReferenceProperty(Scenario, required=True, collection_name='transactions')


class TransactionEntry(PolyModel):
    transaction = ReferenceProperty(Transaction, required=True, collection_name='transaction_entries')
    amount = IntegerProperty(required=True)

    def partial_balance(self, start, end):
        transaction = self.transaction
        start_date = transaction.start_date > start and transaction.start_date or start
        end_date = transaction.end_date < end and transaction.end_date or end
        delta_days = (end_date - start_date).days
        if delta_days < 0:
            return 0.
        if (transaction.end_date - transaction.start_date).days == 0:
            return self.amount
        return self.amount / (transaction.end_date - transaction.start_date).days * delta_days


class AccountingTransactionEntry(TransactionEntry):
    account = ReferenceProperty(Account, required=True, collection_name='transaction_entries')
    item_set = ReferenceProperty(ItemSet, required=True, collection_name='transaction_entries')

class InventoryTransactionEntry(TransactionEntry):
    item_set = ReferenceProperty(ItemSet, required=True, collection_name='inventory_transaction_entries')


def user_scenarios(user, limit=None):
    Scenario.all().filter('owner =', user).fetch(limit)
