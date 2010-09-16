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

    def cumulative_buy(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price for t in trades if t.amount > 0.)

    def cumulative_sell(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.seller_value for t in trades if t.amount < 0.)

    def cumulative_spread(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price - t.seller_value for t in trades)

    def estimated_bid(self, date):
        assets = Asset.all().filter('portfolio =', self).fetch(1000)
        return 1. * sum(a.estimated_bid(date) for a in assets)

    def estimated_ask(self, date):
        assets = Asset.all().filter('portfolio =', self).fetch(1000)
        return 1. * sum(a.estimated_ask(date) for a in assets)

    def __repr__(self):
        return u'<%s object name=%r owner=%r>' % \
            (self.__class__.__name__, self.name, self.owner.nickname())

class Account(Model):
    name = StringProperty(required=True)
    group_under = SelfReferenceProperty()
    order_number = FloatProperty()

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
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.amount for t in trades)

    def cumulative_buy(self, date):
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price for t in trades if t.amount > 0.)

    def cumulative_spread(self, date):
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.buyer_price - t.seller_value for t in trades)

    def cumulative_sell(self, date):
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.seller_value for t in trades if t.amount < 0.)

    def estimated_bid(self, date):
        return 100.0

    def estimated_ask(self, date):
        return 110.0

    def __repr__(self):
        if self.has_identity:
            identification = u'identity=%r' % self.identity
        else:
            identification = u''
        return u'<%s object name=%r %s portfolio=%r owner=%r>' % \
            (self.__class__.__name__, self.name, identification,
                self.portfolio.name, self.portfolio.owner.nickname())

class Trade(Model):
    """A representation of a financial/commercial trade that includes the spread
    between buyer_price and seller_value due to taxes, fees, etc.

    The basic idea is to separate total price paid by the seller in the
    transaction from what the seller actually receives."""

    asset = ReferenceProperty(Asset, required=True, collection_name='trades')
    amount = FloatProperty(required=True)
    date = DateProperty(required=True)
    buyer_price = FloatProperty(required=True)
    seller_value = FloatProperty(default=0.)
    description = TextProperty()

    @property
    def id(self):
        return self.key().id()

class YearlyIncomeExpenses(Model):
    """"""
    name = StringProperty(required=True)
    end_date = DateProperty()
    yearly_income_expense = FloatProperty()
    is_estimated = BooleanProperty(default=False)
    description = TextProperty()
    asset = ReferenceProperty(Asset, required=True, collection_name='yearly_income_expenses')

class Liability(Model):
    owner = UserProperty()
    name = StringProperty(required=True)
    group_under = SelfReferenceProperty()
    outstanding_debt = FloatProperty()
    market_price = FloatProperty()

    def __repr__(self):
        return u'<%s object name="%s" owner="%s">' % \
            (self.__class__.__name__, self.name, self.owner.nickname())
