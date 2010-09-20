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

    def setup_skel(self):
        if list(self.assets):
            return
        eur = Asset(portfolio=self, asset_model=AssetModel.get_by_id(1005), name='Cash EUR', identity='EUR')
        eur.put()
        usd = Asset(portfolio=self, asset_model=AssetModel.get_by_id(1005), name='Cash USD', identity='USD')
        usd.put()
        gold = Asset(portfolio=self, asset_model=AssetModel.get_by_id(1005), name='Cash GOLD', identity='GOLD')
        gold.put()
        for definition in AccountDefinition.all():
            account = Account(definition=definition, denomination=eur)
            account.put()

    def accounts(self):
        return Account.all().filter('denomination IN', list(self.assets))

    def cumulative_buy(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price for t in trades if t.amount > 0.)

    def cumulative_sell(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.seller_value for t in trades if t.amount < 0.)

    def cumulative_spread(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price - t.seller_value for t in trades)

    def estimated_bid(self, date):
        return 1. * sum(a.estimated_bid(date) for a in self.assets)

    def estimated_ask(self, date):
        return 1. * sum(a.estimated_ask(date) for a in self.assets)

    def estimated_yearly_income_expenses(self, date):
        return sum(a.estimated_yearly_income_expenses(date) for a in self.assets)

    def __repr__(self):
        return u'<%s object name=%r owner=%r>' % \
            (self.__class__.__name__, self.name, self.owner.nickname())

class AssetModel(Model):
    name = StringProperty(required=True)
    description = TextProperty()

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

    def buy(self, amount=1., price=None, **keys):
        self.trade(amount=amount, buyer_price=price, **keys)

    def sell(self, amount=1., value=0., **keys):
        self.trade(amount=-amount, seller_value=value, **keys)

    def trade(self, buyer_price=None, seller_value=None, taxes=0., fees=0., **keys):
        if buyer_price is None and seller_value is not None:
            buyer_price = seller_value + taxes + fees
        elif seller_value is None and buyer_price is not None:
            seller_value = buyer_price - taxes - fees
        trade = Trade(asset=self, buyer_price=buyer_price, seller_value=seller_value, **keys)
        trade.put()

    def balance(self, date):
        trades = self.trades.filter('date <=', date)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.amount for t in trades)

    def cumulative_buy(self, date):
        trades = self.trades.filter('date <=', date)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price for t in trades if t.amount > 0.)

    def cumulative_spread(self, date):
        trades = self.trades.filter('date <=', date)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price - t.seller_value for t in trades)

    def cumulative_sell(self, date):
        trades = self.trades.filter('date <=', date)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.seller_value for t in trades if t.amount < 0.)

    def estimated_bid(self, date):
        return 100.0

    def estimated_ask(self, date):
        return 110.0

    def estimated_yearly_income_expenses(self, date):
        return sum(r.yearly_income_expenses for r in self.yearly_income_expenses if r.end_date is None or r.end_date > date)

    def __repr__(self):
        if self.has_identity:
            identification = u'identity=%r' % self.identity
        else:
            identification = u''
        return u'<%s object name=%r %s portfolio=%r owner=%r>' % \
            (self.__class__.__name__, self.name, identification,
                self.portfolio.name, self.portfolio.owner.nickname())

class AccountDefinition(Model):
    name = StringProperty(required=True)
    description = TextProperty()
    parent_account = SelfReferenceProperty()

    @property
    def id(self):
        return self.key().id()

class Account(Model):
    definition = ReferenceProperty(AccountDefinition, required=True, collection_name='accounts')
    denomination = ReferenceProperty(Asset, required=True, collection_name='accounts')

    def balance(self, date):
        return sum(te.amount for te in self.transaction_entries if te.transaction.data <= date)

class Transaction(Model):
    date = DateProperty(required=True)
    description = TextProperty()

    def is_balanced(self):
        return sum(te.amount for te in self.transaction_entries) is 0.

    def add_entries(self, entries):
        balance = sum(te.amount for te in self.transaction_entries) + sum(e[1] for e in entries)
        if balance is not 0.:
            raise ValueError('Unbalanced transaction: %r' % balance)
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

    asset = ReferenceProperty(Asset, required=True, collection_name='trades')
    date = DateProperty(required=True)
    amount = FloatProperty(required=True)
    buyer_price = FloatProperty(required=True)
    seller_value = FloatProperty(default=0.)
    description = TextProperty()

    @property
    def id(self):
        return self.key().id()

class YearlyIncomeExpenses(Model):
    """"""
    asset = ReferenceProperty(Asset, required=True, collection_name='yearly_income_expenses')
    name = StringProperty(required=True)
    end_date = DateProperty()
    yearly_income_expenses = FloatProperty()
    is_estimated = BooleanProperty(default=False)
    description = TextProperty()

    @property
    def id(self):
        return self.key().id()

    def start_date(self):
        return '1999-01-01'

