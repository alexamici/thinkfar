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
    description = StringProperty()

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
    description = StringProperty()
    long_description = TextProperty()

    def __repr__(self):
        return u'<%s object name=%r description=%r>' % \
            (self.__class__.__name__, self.name, self.description)

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

    # FIXME: on a sell you may not care about the buyer total price
    #   price should really be value
    def sell(self, amount=1., price=0., **keys):
        self.trade(amount=-amount, buyer_price=price, **keys)

    def trade(self, taxes=0., commissions=0., **keys):
        trade = Trade(asset=self, **keys)
        if 'value' not in keys:
            trade.set_value_from_price(taxes=taxes, commissions=commissions)
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
        return 100.0

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

    @property
    def id(self):
        return self.key().id()

    def set_value_from_price(self, taxes=0., commissions=0.):
        self.seller_value = self.buyer_price - taxes - commissions

class EstimatedValue(Model):
    """Estimated value including ask/bid spread"""
    estimated_value_date = DateProperty()
    estimated_value_ask = FloatProperty()
    estimated_value_bid = FloatProperty()

class Liability(Model):
    owner = UserProperty()
    name = StringProperty(required=True)
    group_under = SelfReferenceProperty()
    outstanding_debt = FloatProperty()
    market_price = FloatProperty()

    def __repr__(self):
        return u'<%s object name="%s" owner="%s">' % \
            (self.__class__.__name__, self.name, self.owner.nickname())
