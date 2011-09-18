
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from .inventory import User, Book


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.0'


# resource limits
book_itemsets_limit = 100


def extjs_rest(func):
    def extjs_rest_wrapper(request):
        start = int(request.params.get('start', 0) or 0)
        limit = int(request.params.get('limit', 25) or 25)
        page = int(request.params.get('page', 1) or 1)
        return func(request, page=page, start=start, limit=limit)
    return extjs_rest_wrapper


@view_config(route_name='books_json', renderer='json', request_method='GET')
@extjs_rest
def books_json(request, page=1, start=0, limit=25):
    user_uid = request.matchdict['user_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    books = user.books.fetch(min(limit, Book.user_books_limit), offset=start)
    retval = [
        {
            'uid': book.uid,
            'name': book.name, 
            'accounting_universe_uid': book.accounting_universe.uid,
            'inventory_count': book.inventory.count(),
        } for book in books
    ]
    return retval


@view_config(route_name='inventory_json', renderer='json', request_method='GET')
@extjs_rest
def inventory_json(request, page=1, start=0, limit=25):
    user_uid = request.matchdict['user_uid']
    book_uid = request.matchdict['book_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    books = user.books.filter('uid =', book_uid).fetch(2)
    if len(books) != 1:
        raise HTTPNotFound
    itemsets = books[0].inventory.fetch(min(limit, book_itemsets_limit), offset=start)
    retval = [
        {
            'uid': itemset.uid,
            'name': itemset.name, 
            'accounting_universe_uid': itemset.item_class.uid,
            'inventory_count': itemset.balance(),
        } for itemset in itemsets
    ]
    return retval
