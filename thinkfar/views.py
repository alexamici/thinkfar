
from simplejson import dumps

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from .inventory import User, AccountingUniverse


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.0'


@view_config(request_method='GET')
def root_view(request):
    return Response('<h1>Think-Far!</h1>')

@view_config(route_name='accounting_universe_index_html', request_method='GET')
def accounting_universe_index_html(request):
    accounting_universe_uid = request.matchdict['accounting_universe_uid']
    accounting_universe = AccountingUniverse.get_by_key_name(accounting_universe_uid)
    if accounting_universe is None:
        raise HTTPNotFound
    return Response(dumps((accounting_universe.uid, accounting_universe.name)))


@view_config(route_name='book_index_html', request_method='GET')
def book_index_html(request):
    user_uid = request.matchdict['user_uid']
    book_uid = request.matchdict['book_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    books = user.books.filter('uid =', book_uid).fetch(1)
    if len(books) != 1:
        raise HTTPNotFound
    return Response(dumps((books[0].uid, books[0].name)))


@view_config(route_name='user_index_html', request_method='GET')
def user_index_html(request):
    user_uid = request.matchdict['user_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    return Response(dumps((user.uid, user.principal.email(), user.principal.user_id())))
