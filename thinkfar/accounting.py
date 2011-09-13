"""
'Price is what you pay. Value is what you get.' Warren Buffett, 2008.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import BooleanProperty, IntegerProperty, DateProperty
from google.appengine.ext.db import TextProperty, StringProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty
from google.appengine.ext.db.polymodel import PolyModel

from .importexport import load_items
from .inventory import ItemSet, AccountingUniverse


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


class GenericAccount(PolyModel):
    uid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()


class TotalAccount(GenericAccount):
    is_asset = BooleanProperty(default=False)
    is_liability = BooleanProperty(default=False)
    is_revenue = BooleanProperty(default=False)
    is_expense = BooleanProperty(default=False)

    accounting_universe = ReferenceProperty(AccountingUniverse, collection_name='total_accounts')

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

    def transaction_templates_uids(self):
        return sorted(tt.uid for tt in self.transaction_templates)

    def transaction_template(self, uid):
        for tt in self.transaction_templates:
            if tt.uid == uid:
                return tt
        else:
            raise KeyError(uid)


class TransactionTemplate(Model):
    item_class = ReferenceProperty(ItemClass, required=True, collection_name='transaction_templates')

    uid = StringProperty(required=True)
    name = StringProperty()
    description = TextProperty()

    template_type = StringProperty(required=True,
        choices=['buy', 'sell', 'yearly_costs', 'yearly_revenues'])
    template_definition = StringProperty(required=True)


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
            return 0
        if (transaction.end_date - transaction.start_date).days == 0:
            return self.amount
        return self.amount / (transaction.end_date - transaction.start_date).days * delta_days

    def balance(self, date):
        return self.partial_balance(self, self.transaction.start_date, date)


class AccountingTransactionEntry(TransactionEntry):
    account = ReferenceProperty(Account, required=True, collection_name='transaction_entries')
    item_set = ReferenceProperty(ItemSet, required=True, collection_name='transaction_entries')


def user_scenarios(user, limit=None):
    Scenario.all().filter('owner =', user).fetch(limit)


def load_accounting_tree(root, accounting_tree):
    load_items(TotalAccount, accounting_tree,
        key_prefix=root.uid + '/', accounting_universe=root,
        children_classes=[AggregateAccount, Account])

