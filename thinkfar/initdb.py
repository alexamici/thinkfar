
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
    poor = setup_average_joe_base_portfolio('Poor Joe Portfolio')
    average = setup_average_joe_base_portfolio('Average Joe Portfolio')
    middle_class = setup_average_joe_base_portfolio('Middle-class Joe Portfolio')

def setup_average_joe_base_portfolio(name):
    joe_p = Portfolio(start_date=date(1970, 1, 1), name=name, owner=get_current_user())
    joe_p.put()

    working_time = Asset(name='Joe Working Time',
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Time'))
    working_time.put()
    working_time.buy(amount=45*11*21*8., price=5.*45*11*21*8.)
    working_time.sell(amount=45*11*21*8., value=5.*45*11*21*8., date=date(1995, 1, 1), end_date=date(2040, 1, 1),
        debit_account=joe_p.default_equity_account)

    job = Asset(name='Joe Job', description="Plumber",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Job'))
    job.put()
    job.buy(date=date(1995, 6, 1), price=1.*44*11*21*8, debit_account=joe_p.default_equity_account)
    job.add_ammortization(value=1.*44*11*21*8, date=date(1995, 6, 1), end_date=date(2039, 6, 1),
        debit_account=joe_p.default_equity_account)
    job.add_revenue(start_date=date(1995, 6, 1), end_date=date(2039, 6, 1), revenue=6.*44*11*21*8)
    shelter_need = Asset(name='Joe Food&Shelter Needs', portfolio=joe_p, asset_model=AssetModel.get_by_name('Need'))
    shelter_need.put()
    shelter_need.buy(amount=65*12., price=-600.*65*12.)
    shelter_need.sell(amount=65*12., value=-600.*65*12., date=date(1995, 1, 1), end_date=date(2060, 1, 1),
        debit_account=joe_p.default_equity_account)
    shelter_need.add_revenue(start_date=date(1995, 1, 1), end_date=date(2060, 1, 1), revenue=-600.*65*12.)
