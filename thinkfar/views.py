
from google.appengine.api.users import get_current_user, create_login_url, create_logout_url

from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config

from .inventory import User, AccountingUniverse


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.0'


def init_namespace():
    current_user = get_current_user()
    loggedin_url = current_user and create_logout_url('/') or create_login_url('/')
    loggedin_label = current_user and ('Log out %s' % current_user.nickname()) or 'Log in'
    title = 'thinkfar'
    main = get_renderer('templates/main.pt').implementation()
    return locals()


def common_template(view):
    namespace = init_namespace()
    def wrapped_view(request):
    	return view(request, namespace)    
    return wrapped_view


@view_config(request_method='GET', renderer='templates/main.pt')
@common_template
def index_html(request, init_namespace):
    return init_namespace


@view_config(route_name='accounting_universe_index_html', request_method='GET')
@common_template
def accounting_universe_index_html(request):
    accounting_universe_uid = request.matchdict['accounting_universe_uid']
    accounting_universe = AccountingUniverse.get_by_key_name(accounting_universe_uid)
    if accounting_universe is None:
        raise HTTPNotFound
    return Response('OK')


@view_config(route_name='book_index_html', request_method='GET', renderer='templates/book_index_html.pt')
@common_template
def book_index_html(request, init_namespace):
    user_uid = request.matchdict['user_uid']
    book_uid = request.matchdict['book_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    books = user.books.filter('uid =', book_uid).fetch(2)
    if len(books) != 1:
        raise HTTPNotFound
    namespace = init_namespace.copy()
    namespace.update({'user': user, 'book': books[0]})
    return namespace


@view_config(route_name='user_index_html', request_method='GET', renderer='templates/user_index_html.pt')
@common_template
def user_index_html(request, init_namespace):
    user_uid = request.matchdict['user_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    namespace = init_namespace.copy()
    namespace.update({'user': user})
    return namespace
