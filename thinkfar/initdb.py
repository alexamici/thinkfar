
from datetime import date

from google.appengine.api.users import get_current_user

from .models import Portfolio, Asset, AssetModel, AccountDefinition

def drop_kind(kindname):
    from google.appengine.ext import db
    from time import sleep

    while True:
        q = db.GqlQuery("SELECT __key__ FROM %s" % (kindname,))
        if q.count() == 0:
            break
        db.delete(q.fetch(200))
        sleep(0.5)

def load_kind(kind, instances_keys=None, parent_instance=None):
    if instances_keys is None:
        instances_keys = kind.base_instances_keys
    for keys in instances_keys:
        children = keys.pop('children', ())
        keys['parent_account'] = parent_instance
        for attr in ('is_asset', 'is_liability', 'is_revenue', 'is_expense'):
            try:
                keys[attr] = getattr(parent_instance, attr)
            except:
                pass
        instance = kind(**keys)
        instance.put()
        load_kind(kind, instances_keys=children, parent_instance=instance)

def initdb():
    # drop instances of all kinds
    for kindname in ('Portfolio', 'AssetModel', 'Asset',
            'AccountDefinition', 'Account', 'Transaction', 'TransactionEntry'):
        drop_kind(kindname)
    # create objects assumed to be present
    for kind in (AssetModel, AccountDefinition):
        load_kind(kind)

def setup_test_portfolios():
    try:
        from averagejoe import setup_average_joe_portfolio
    except ImportError:
        global setup_average_joe_portfolio
    setup_average_joe_portfolio()

def setup_average_joe_portfolio():
    joe_p = Portfolio(name="Average Joe Portfolio", owner=get_current_user())
    joe_p.put()
    land1 = Asset(name='Joe Field 1', portfolio=joe_p, asset_model=AssetModel.get_by_name('Land'))
    land1.put()
    land1.buy(price=10000.)
    land2 = Asset(name='Joe Field 2', portfolio=joe_p, asset_model=AssetModel.get_by_name('Land'))
    land2.put()
    land2.buy(price=8000.)
    home = Asset(name='Joe Home', description="2350 Sweet Home Road, Amherst, NY, United States",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Building'))
    home.put()
    home.buy(date=date(2001, 12, 21), price=150000.)
    home.add_yearly_revenue(8400.)
    home.add_yearly_revenue(-1000., code='9180')
    mortgage = Asset(name='Joe Home Mortgage', description="Lien on 2350 Sweet Home Road, Amherst, NY, United States",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Mortgage'))
    mortgage.put()
    mortgage.buy(date=date(2001, 12, 21), price=-100000.)
    mortgage.add_yearly_revenue(-7000., code='8710')
    job = Asset(name='Joe Job', description="Plumber",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Job'))
    job.put()
    job.buy(date=date(2001, 6, 1), price=0.)
    job.add_yearly_revenue(28000.)
    job.add_yearly_revenue(-9000., code='8764')
    cc = Asset(name='Joe Credit Card', description="Average Bank",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Credit Card'))
    cc.put()
    cc.buy(amount=1., price=-5000., date=date(2002, 8, 1))
    cc.add_yearly_revenue(-5000.*.13, code='8710')
    gold = Asset.all().filter('portfolio =', joe_p).filter('identity =', 'GOLD').fetch(1)[0]
    gold.buy(amount=2., price=600.)
