

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
        return 1. * sum(t.price for t in trades if t.ammount > 0.)

    def cumulative_sell(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.price for t in trades if t.ammount < 0.)

    def cumulative_cost(self, date):
        trades = Trade.all().filter('asset IN', list(self.assets)).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.cost for t in trades)

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

    def buy(self, ammount=1., **keys):
        self.trade(ammount=ammount, **keys)

    def sell(self, ammount=1., price=0., **keys):
        self.trade(ammount=-ammount, price=price, **keys)

    def trade(self, **keys):
        trade = Trade(asset=self, **keys)
        trade.put()

    def balance(self, date):
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.ammount for t in trades)

    def cumulative_buy(self, date):
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.price for t in trades if t.ammount > 0.)

    def cumulative_cost(self, date):
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.cost for t in trades)

    def cumulative_sell(self, date):
        trades = Trade.all().filter('asset =', self.key()).filter('date <=', date).fetch(1000)
        # return float 0. if no trades for the sake of consistency
        return 1. * sum(t.price for t in trades if t.ammount < 0.)

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
    """Asset trade"""
    asset = ReferenceProperty(Asset, required=True, collection_name='trades')
    ammount = FloatProperty(required=True)
    date = DateProperty(required=True)
    price = FloatProperty(required=True)
    cost = FloatProperty(default=0.)

    @property
    def id(self):
        return self.key().id()

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
