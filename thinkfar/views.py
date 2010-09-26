
from datetime import date

from google.appengine.api.users import get_current_user, create_login_url, create_logout_url
from repoze.bfg.chameleon_zpt import get_template
from webob.exc import HTTPUnauthorized
from webob import Response

from .models import Portfolio, Asset, AssetModel, AccountDefinition, Transaction


# global limits
per_user_portfolio_limit = 10


def common_namespace(request):
    user = get_current_user()
    loggedin_url = user and create_logout_url('/') or create_login_url('/')
    loggedin_label = user and 'Log out' or 'Log in'
    main = get_template('templates/main.pt')
    namespace = {'loggedin_url': loggedin_url, 'loggedin_label': loggedin_label,
        'user': user, 'main': main}
    return namespace

def root_view(context, request):
    namespace = common_namespace(request)
    portfolios = Portfolio.all().filter('owner =', namespace['user']).fetch(per_user_portfolio_limit)
    namespace.update({'portfolios': portfolios, 'title': context.title})
    return namespace

def portfolio_default(request):
    namespace = common_namespace(request)
    id = int(request.matchdict['id'])
    portfolio = Portfolio.get_by_id(id)
    if portfolio is None or portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    today = date.today()
    namespace.update({'context': portfolio, 'portfolio': portfolio, 'date': today, 
        'title': '%s -> %s' % (portfolio.owner.nickname(), portfolio.name)})
    return namespace

def portfolio_balance(request):
    namespace = portfolio_default(request)
    return namespace

portfolio_income = portfolio_default

def asset_view(request):
    namespace = common_namespace(request)
    id = int(request.matchdict['id'])
    asset = Asset.get_by_id(id)
    if asset is None or asset.portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    today = date.today()
    def date_cmp(x, y):
        return (x.transaction.date - y.transaction.date).days
    inventory_transaction_entries = sorted(asset.inventory.transaction_entries, date_cmp)
    parent_account_transaction_entries = sorted(asset.parent_account.transaction_entries, date_cmp)
    namespace.update({'project': 'thinkfar', 'asset': asset, 'date': today, 
        'title': '%s -> %s -> %s' % (asset.portfolio.owner.nickname(), asset.portfolio.name, asset.name),
        'inventory_transaction_entries': inventory_transaction_entries,
        'parent_account_transaction_entries': parent_account_transaction_entries})
    return namespace

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
        instance = kind(**keys)
        instance.put()
        load_kind(kind, instances_keys=children, parent_instance=instance)

def initdb():
    # drop instances of all kinds
    for kindname in ('Portfolio', 'AssetModel', 'Asset',
            'AccountDefinition', 'Account', 'Transaction', 'TransactionEntry', 'Trade'):
        drop_kind(kindname)
    # create objects assumed to be present
    for kind in (AssetModel, AccountDefinition):
        load_kind(kind)

def initdb_view(request):
    initdb()
    return Response(body='Done')


def setup_test_portfolios(request):
    joe_p = Portfolio(name="Average Joe Portfolio", owner=get_current_user())
    joe_p.put()
    joe_p.default_cash_asset.buy(amount=1., price=100000.)
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
    home.add_revenue_account(code='8141', yearly_revenue=12000.)
    mortgage = Asset(name='Joe Home Mortgage', description="Lien on 2350 Sweet Home Road, Amherst, NY, United States",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Mortgage'))
    mortgage.put()
    mortgage.buy(date=date(2001, 12, 21), price=-100000.)
    mortgage.add_revenue_account(code='8710', yearly_revenue=-100000.*.07)
    job = Asset(name='Joe Job', description="Plumber",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Job'))
    job.put()
    job.buy(date=date(2001, 6, 1), price=0.)
    job.add_revenue_account(code='8000', yearly_revenue=25000.)
    cc = Asset(name='Joe Credit Card', description="Average Bank",
        portfolio=joe_p, asset_model=AssetModel.get_by_name('Credit Card'))
    cc.put()
    cc.buy(amount=1., price=-5000., date=date(2002, 8, 1))
    cc.add_revenue_account(code='8710', yearly_revenue=-5000.*.13)
    gold = Asset.all().filter('portfolio =', joe_p).filter('identity =', 'GOLD').fetch(1)[0]
    gold.buy(amount=2., price=600.)
    return Response(body='Done')
