
from simplejson import dumps

from google.appengine.api.users import get_current_user, create_login_url, create_logout_url

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from .inventory import User, AccountingUniverse


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.0'


@view_config(request_method='GET', renderer='templates/main.pt')
def index_html(request):
    user = get_current_user()
    loggedin_url = user and create_logout_url('/') or create_login_url('/')
    loggedin_label = user and ('Log out %s' % user.nickname()) or 'Log in'
    namespace = {'loggedin_url': loggedin_url, 'loggedin_label': loggedin_label,
        'title': 'Home'}
    return namespace


@view_config(route_name='accounting_universe_index_html', request_method='GET')
def accounting_universe_index_html(request):
    accounting_universe_uid = request.matchdict['accounting_universe_uid']
    accounting_universe = AccountingUniverse.get_by_key_name(accounting_universe_uid)
    if accounting_universe is None:
        raise HTTPNotFound
    return Response(dumps((accounting_universe.uid, accounting_universe.name)))


@view_config(route_name='book_index_html', request_method='GET', renderer='templates/book_index_html.pt')
def book_index_html(request):
    user_uid = request.matchdict['user_uid']
    book_uid = request.matchdict['book_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    books = user.books.filter('uid =', book_uid).fetch(2)
    if len(books) != 1:
        raise HTTPNotFound
    return {'user': user, 'book': books[0]}


@view_config(route_name='user_index_html', request_method='GET', renderer='templates/user_index_html.pt')
def user_index_html(request):
    user_uid = request.matchdict['user_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    return {'user': user}
