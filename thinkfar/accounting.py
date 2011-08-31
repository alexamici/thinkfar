"""
'Price is what you pay. Value is what you get.' Warren Buffett, 2008.
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import BooleanProperty, FloatProperty, DateProperty
from google.appengine.ext.db import TextProperty, StringProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty
from google.appengine.ext.db.polymodel import PolyModel


class AccountClass(Model):
	"""
	Abstract definition of an accounts tree

	Accounts trees are global and shared between all users.
	Only a root account has no parent_account and scenarios
	should point to a root account.
	"""
	uuid = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()

    parent_account = SelfReferenceProperty(collection_name='children_accounts')

    is_asset = BooleanProperty(default=False)
    is_liability = BooleanProperty(default=False)
    is_revenue = BooleanProperty(default=False)
    is_expense = BooleanProperty(default=False)

   	@property
    def is_balance_sheet(self):
        return self.is_asset or self.is_liability


class Transaction(Model):
	"""An event in the double-entry book

    The transaction may have an time extension and in that case it 
    really correspondes to a linear change in the account balances.
    """
    uid = StringProperty(required=True)
    name = StringProperty()
    description = TextProperty()

    start_date = DateProperty(required=True)
    end_date = DateProperty(required=True)


class TransactionEntry(PolyModel):
	transaction = ReferenceProperty(Transaction, required=True, collection_name='transaction_entries')
	amount = IntegerProperty(required=True)

	def entry_partial_balance(self, start, end):
	     transaction = self.transaction
	     start_date = transaction.start_date > start_date and transaction.start_date or start_date
	     end_date = transaction.end_date < end_date and transaction.end_date or end_date
	     delta_days = (end_date - start_date).days
	     if delta_days < 0:
	         return 0.
	     if (transaction.end_date - transaction.start_date).days == 0:
	         return self.amount
	     return self.amount / (transaction.end_date - transaction.start_date).days * delta_days


class AccountingTransactionEntry(TransactionEntry):
	account = ReferenceProperty(AccountClass, required=True, collection_name='transactions')


class Scenario(Model):
	owner = UserProperty(required=True)

    name = StringProperty(required=True, default=u'Default Portfolio')
    description = TextProperty()

	start_date = DateProperty(required=True)


def user_scenarios(user, limit=None):
	Scenario.all().filter('owner =', user).fetch(limit)
