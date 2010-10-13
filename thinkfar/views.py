
from datetime import date

from google.appengine.api.users import get_current_user, create_login_url, create_logout_url
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.url import route_url
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
    try:
        ref_date = date(*(int(t) for t in request.params.get('date').split('-')))
    except:
        ref_date = date.today()
    main = get_template('templates/main.pt')
    namespace = {'loggedin_url': loggedin_url, 'loggedin_label': loggedin_label,
        'user': user, 'main': main, 'route_url': route_url, 'date': ref_date}
    return namespace

def root_view(context, request):
    namespace = common_namespace(request)
    portfolios = Portfolio.all().filter('owner =', namespace['user']).fetch(per_user_portfolio_limit)
    namespace.update({'portfolios': portfolios, 'title': context.title})
    return namespace

def portfolio_default(request):
    namespace = common_namespace(request)
    id = int(request.matchdict['portfolio_id'])
    portfolio = Portfolio.get_by_id(id)
    if portfolio is None or portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    namespace.update({'context': portfolio, 'portfolio': portfolio,
        'title': '%s -> %s' % (portfolio.owner.nickname(), portfolio.name)})
    return namespace

def portfolios_rest(request):
    if request.method not in ('GET',):
        raise NotImplementdError
    try:
        ref_date = date(*(int(t) for t in request.params.get('date')[:10].split('-')))
    except:
        ref_date = date.today()
    start = int(request.params.get('start', 0) or 0)
    limit = int(request.params.get('limit', 25) or 25)
    query = Portfolio.all().filter('owner =', get_current_user()).order('name')
    rows = []
    for portfolio in query.fetch(limit, offset=start):
        rows.append({
            'url': route_url('portfolio_default', request, portfolio_id=portfolio.id),
            'name': portfolio.name,
            'total_value': portfolio.total_value(ref_date), 
            'yearly_revenue': portfolio.estimated_yearly_revenue(ref_date.year), 
        })
    return {'total': query.count(), 'success': True, 'rows': rows, 'start': start, 'limit': limit}

def portfolio_rest(request):
    return {}

def assets_rest(request):
    if request.method not in ('GET',):
        raise NotImplementdError
    id = int(request.matchdict['portfolio_id'])
    portfolio = Portfolio.get_by_id(id)
    if portfolio is None or portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    try:
        ref_date = date(*(int(t) for t in request.params.get('date')[:10].split('-')))
    except:
        ref_date = date.today()
    start = int(request.params.get('start', 0) or 0)
    end = start + int(request.params.get('limit', 25) or 25)
    data = []
    count = 0
    for asset in portfolio.assets.order('name'):
        if asset.inventory.balance(ref_date) == 0:
            continue
        if count < start:
            count += 1
            continue
        if count < end:
            data.append({
                'url': route_url('asset_default', request,
                    portfolio_id=portfolio.id, asset_id=asset.id),
                'name': asset.name,
                'inventory': asset.inventory.balance(ref_date),
                'total_value': asset.total_value(ref_date), 
                'yearly_revenue': asset.estimated_yearly_revenue(ref_date.year),
            })
        count += 1
    return {'total': count, 'success': True, 'rows': data, 'start': start, 'limit': end - start}

def portfolio_balance(request):
    namespace = portfolio_default(request)
    return namespace

portfolio_income = portfolio_estimated_income = portfolio_default 

def asset_default(request):
    namespace = common_namespace(request)
    id = int(request.matchdict['asset_id'])
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

def accounts_rest(request):
    if request.method not in ('GET',):
        raise NotImplementdError
    id = int(request.matchdict['portfolio_id'])
    portfolio = Portfolio.get_by_id(id)
    if portfolio is None or portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    try:
        ref_date = date(*(int(t) for t in request.params.get('date')[:10].split('-')))
    except:
        ref_date = date.today()
    start = int(request.params.get('start', 0) or 0)
    end = start + int(request.params.get('limit', 50) or 50)
    in_balance_sheet = 'true' is (request.params.get('in_balance_sheet', 'true') or 'true')
    rows = []
    count = 0
    for total_account in portfolio.total_accounts():
        if total_account.definition.in_balance_sheet != in_balance_sheet:
            continue
        for aggregate_account in total_account.children_accounts:
            for asset_account in aggregate_account.children_accounts:
                if asset_account.balance(ref_date) == 0:
                    continue
                if count < start:
                    count += 1
                    continue
                if count < end:
                    rows.append({
                        'url': route_url('account_default', request,
                            portfolio_id=portfolio.id, account_id=asset_account.id),
                        'name': asset_account.definition.name,
                        'denomination_identity': asset_account.denomination.identity,
                        'asset_balance': asset_account.sign_balance(ref_date),
                    })
                count += 1
            if count < start:
                count += 1
                continue
            if count < end:
                rows.append({
                    'url': route_url('account_default', request,
                        portfolio_id=portfolio.id, account_id=aggregate_account.id),
                    'name': aggregate_account.definition.name,
                    'denomination_identity': aggregate_account.denomination.identity,
                    'aggregate_balance': aggregate_account.sign_balance(ref_date),
                })
            count += 1
        if count < start:
            count += 1
            continue
        if count < end:
            rows.append({
                'url': route_url('account_default', request,
                    portfolio_id=portfolio.id, account_id=total_account.id),
                'name': total_account.definition.name,
                'denomination_identity': total_account.denomination.identity,
                'total_balance': total_account.sign_balance(ref_date),
            })
        count += 1
    if in_balance_sheet is True:
        revenue, expenses = portfolio.total_income_statment_accounts()
        rows.append({
            'url': '#',
            'name': 'Current Profit/Loss',
            'denomination_identity': revenue.denomination.identity,
            'total_balance': revenue.sign_balance(ref_date) - expenses.sign_balance(ref_date),
        })
    return {'total': count, 'success': True, 'rows': rows, 'start': start, 'limit': end - start}

def account_default(request):
    return {}
    
def transaction_default(request):
    return {}

def initdb_view(request):
    initdb()
    return Response(body='initdb done')

def setup_test_portfolios_view(request):
    setup_test_portfolios()
    return Response(body='setup_test_portfolios done')
