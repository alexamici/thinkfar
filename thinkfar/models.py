# 'Price is what you pay. Value is what you get.' Warren Buffett, 2008.

from google.appengine.ext.db import Model, FloatProperty, StringProperty, BooleanProperty
from google.appengine.ext.db import TextProperty, DateProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty


class Root(object):
    title = u'think beyond the end of your nose'

root = Root()

def get_root(request):
    return root


class Portfolio(Model):
    owner = UserProperty(required=True)
    name = StringProperty(required=True, default=u'Default Portfolio')
    description = TextProperty()

    @property
    def id(self):
        return self.key().id()

    def put(self):
        if self.is_saved():
            return super(Portfolio, self).put()
        key = super(Portfolio, self).put()
        currency = AssetModel.all().filter('name =', 'Currency').fetch(1)[0]
        eur = Asset(portfolio=self, asset_model=currency, name='Cash EUR', identity='EUR')
        eur.put()
        usd = Asset(portfolio=self, asset_model=currency, name='Cash USD', identity='USD')
        usd.put()
        gold = Asset(portfolio=self, asset_model=currency, name='Cash GOLD', identity='GOLD')
        gold.put()
        for definition in AccountDefinition.all():
            account = Account(definition=definition, denomination=eur)
            account.put()
        return key

    def accounts(self):
        return Account.all().filter('denomination IN', list(self.assets))

    def __repr__(self):
        return u'<%s object name=%r owner=%r>' % \
            (self.__class__.__name__, self.name, self.owner.nickname())

class AssetModel(Model):
    name = StringProperty(required=True)
    description = TextProperty()
    parent_account_code = StringProperty()

    base_instances = (
        {'name': 'Currency', 'parent_account_code': '1001'},
        {'name': 'Land', 'parent_account_code': '1600'},
        {'name': 'Building', 'parent_account_code': '1680'},
        {'name': 'Credit Card', 'parent_account_code': '2707'},
    )

    def __repr__(self):
        return u'<%s object name=%r>' % \
            (self.__class__.__name__, self.name)

class Asset(Model):
    """Base asset class"""
    portfolio = ReferenceProperty(Portfolio, required=True, collection_name='assets')
    asset_model = ReferenceProperty(AssetModel, required=True)
    name = StringProperty(required=True)
    identity = StringProperty()
    long_identity = TextProperty()

    @property
    def id(self):
        return self.key().id()

    @property
    def has_identity(self):
        return self.identity is not None

    def put(self):
        if self.is_saved():
            return super(Asset, self).put()
        key = super(Asset, self).put()
        balance = Account(definition=None, denomination=self)
        balance.put()
        return key

    def buy(self, amount=1., price=None, **keys):
        self.trade(amount=amount, buyer_price=price, **keys)

    def sell(self, amount=1., value=0., **keys):
        self.trade(amount=-amount, seller_value=value, **keys)

    def trade(self, buyer_price=None, seller_value=None, taxes=0., fees=0.,
            date=None, amount=None, description=None):
        if buyer_price is None and seller_value is not None:
            buyer_price = seller_value + taxes + fees
        elif seller_value is None and buyer_price is not None:
            seller_value = buyer_price - taxes - fees
        trade = Transaction(date=date, description=description)
        trade.put()
        trade.add_entries(((self.account, amount),))

    @property
    def account(self):
        for a in self.accounts:
            if a.definition is None:
                return a

    def __repr__(self):
        if self.has_identity:
            identification = u'identity=%r' % self.identity
        else:
            identification = u''
        return u'<%s object name=%r %s portfolio=%r owner=%r>' % \
            (self.__class__.__name__, self.name, identification,
                self.portfolio.name, self.portfolio.owner.nickname())

# GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf
class AccountDefinition(Model):
    code = StringProperty(required=True)
    name = StringProperty(required=True)
    description = TextProperty()
    parent_account = SelfReferenceProperty(collection_name='children_accounts')

    base_instances = (
        {'code': '2599', 'name': 'Total assets', 'children': (
            {'code': '1599', 'name': 'Total current assets', 'children': (
                {'code': '1001', 'name': 'Cash'},
            )},
            {'code': '2008', 'name': 'Total tangible capital assets'},
            {'code': '2178', 'name': 'Total intangible capital assets'},
            {'code': '2589', 'name': 'Total long-term assets'},
        )},
        {'code': '3499', 'name': 'Total liabilities'},
        {'code': '3620', 'name': 'Total equity'},
        {'code': '8299', 'name': 'Total revenue'},
        {'code': '9368', 'name': 'Total expenses'},
    )

    @property
    def id(self):
        return self.key().id()

class Account(Model):
    # if definition is None the account is the balance of the denomination asset
    definition = ReferenceProperty(AccountDefinition, collection_name='accounts')
    denomination = ReferenceProperty(Asset, required=True, collection_name='accounts')
    parent_account = SelfReferenceProperty()

    def balance(self, date):
        return sum(te.amount for te in self.transaction_entries if te.transaction.date <= date)

class Transaction(Model):
    date = DateProperty(required=True)
    description = TextProperty()

    def is_balanced(self):
        # transaction_entities belonging to inventory accounts are not balanced
        balanced_transaction_entities = filter(lambda te: te.account.description is not None, self.transaction_entries)
        balanced_denominations = set(te.account.denomination for te in balanced_transaction_entities)
        for d in balanced_denominations:
            balance = sum(te.amount for te in balanced_transaction_entities if te.account.denomination is d)
            if balance:
                return False
        return True

    def add_entries(self, entries):
        balance = sum(te.amount for te in self.transaction_entries) + sum(e[1] for e in entries)
        if balance is not 0.:
            pass
            # raise ValueError('Unbalanced transaction: %r' % balance)
        for e in entries:
            te = TransactionEntry(transaction=self, account=e[0], amount=e[1])
            te.put()

class TransactionEntry(Model):
    transaction = ReferenceProperty(Transaction, required=True, collection_name='transaction_entries')
    account = ReferenceProperty(Account, required=True, collection_name='transaction_entries')
    amount = FloatProperty(required=True)


# OBSOLETE

class Trade(Model):
    """A representation of a financial/commercial trade that includes the spread
    between buyer_price and seller_value due to taxes, fees, etc.

    The basic idea is to separate total price paid by the seller in the
    transaction from what the seller actually receives."""

    @property
    def id(self):
        return self.key().id()
