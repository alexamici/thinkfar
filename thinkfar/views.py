
from datetime import date

from webob.exc import HTTPUnauthorized
from google.appengine.api.users import get_current_user, create_login_url, create_logout_url

from .models import Portfolio, Asset


def login_logout(request):
    current_user = get_current_user()
    login_logout_url = current_user and create_logout_url('/') or create_login_url('/')
    login_logout_label = current_user and 'Log out' or 'Log in'
    namespace = {'login_logout_url': login_logout_url, 'login_logout_label': login_logout_label,
        'current_user': current_user}
    return namespace

def root_view(request):
    namespace = login_logout(request)
    portfolios = Portfolio.all().filter('owner =', namespace['current_user']).fetch(10)
    namespace.update({'project': 'thinkfar', 'portfolios': portfolios})
    return namespace

def portfolio_view(request):
    namespace = login_logout(request)
    id = int(request.matchdict['id'])
    portfolio = Portfolio.get_by_id(id)
    if portfolio is None or portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    today = date.today()
    namespace.update({'project': 'thinkfar', 'portfolio': portfolio, 'date': today})
    return namespace

def asset_view(request):
    namespace = login_logout(request)
    id = int(request.matchdict['id'])
    asset = Asset.get_by_id(id)
    if asset is None or asset.portfolio.owner != get_current_user():
        return HTTPUnauthorized()
    today = date.today()
    namespace.update({'project': 'thinkfar', 'asset': asset, 'date': today})
    return namespace
