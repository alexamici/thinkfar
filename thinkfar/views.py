
from datetime import date

from google.appengine.api.users import get_current_user, create_login_url, create_logout_url
from repoze.bfg.chameleon_zpt import get_template
from webob.exc import HTTPUnauthorized
from webob import Response

from .initdb import initdb, setup_test_portfolios
from .models import Portfolio, Asset

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

portfolio_income = portfolio_estimated_income = portfolio_default 

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
    default_value_account_transaction_entries = sorted(asset.default_value_account.transaction_entries, date_cmp)
    namespace.update({'project': 'thinkfar', 'asset': asset, 'date': today, 
        'title': '%s -> %s -> %s' % (asset.portfolio.owner.nickname(), asset.portfolio.name, asset.name),
        'inventory_transaction_entries': inventory_transaction_entries,
        'default_value_account_transaction_entries': default_value_account_transaction_entries})
    return namespace

def initdb_view(request):
    initdb()
    return Response(body='initdb done')

def setup_test_portfolios_view(request):
    setup_test_portfolios()
    return Response(body='setup_test_portfolios done')
