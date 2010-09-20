
from datetime import date

from google.appengine.api.users import get_current_user, create_login_url, create_logout_url
from repoze.bfg.chameleon_zpt import get_template
from webob.exc import HTTPUnauthorized
from webob import Response

from .models import Portfolio, Asset, AssetModel


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

portfolio_balance = portfolio_income = portfolio_default

def asset_view(request):
    namespace = common_namespace(request)
    id = int(request.matchdict['id'])
    asset = Asset.get_by_id(id)
    if asset is None or asset.portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    today = date.today()
    namespace.update({'project': 'thinkfar', 'asset': asset, 'date': today, 
        'title': '%s -> %s -> %s' % (asset.portfolio.owner.nickname(), asset.portfolio.name, asset.name)})
    return namespace

def setup_test_portfolios(request):
    joe_p = Portfolio(name="Average Joe Portfolio", owner=get_current_user())
    joe_p.put()
    home = Asset(name='Joe Home',description="2350 Sweet Home Road, Amherst, NY, United States",
        portfolio=joe_p, asset_model=AssetModel.get_by_id(1001))
    home.put()
    return Response()
    
