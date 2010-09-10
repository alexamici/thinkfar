
from datetime import date

from google.appengine.api.users import get_current_user

from .models import Portfolio

def home(request):
    portfolios = Portfolio.all().filter('owner =', get_current_user()).fetch(10)
    return {'project': 'thinkfar', 'portfolios': portfolios}

def portfolio(request):
    id = int(request.matchdict['id'])
    portfolio = Portfolio.get_by_id(id)
    today = date.today()
    return {'project': 'thinkfar', 'portfolio': portfolio, 'date': today}
