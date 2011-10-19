
from datetime import date

from webapp2 import RequestHandler, Response
from webapp2_extras.json import encode

# dummy migration helpers
def view_config(*args, **keys):
    return lambda x: None
HTTPNotFound = ValueError

from .inventory import User, Book
from .accounting import AccountingUniverse


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.0'


# resource limits
book_itemsets_limit = 100


def extjs_rest(func):
    def extjs_rest_wrapper(request, *args, **keys):
        start = int(request.get('start', 0) or 0)
        limit = int(request.get('limit', 25) or 25)
        page = int(request.get('page', 1) or 1)
        return func(request, page=page, start=start, limit=limit, *args, **keys)
    return extjs_rest_wrapper


# @view_config(route_name='accounts_json', renderer='json', request_method='GET')

@extjs_rest
def accounts_json(request, accounting_universe_uid, page=1, start=0, limit=25):
    response = Response()
    response.out.write(encode(page))
    accounting_universe = AccountingUniverse.get_by_key_name(accounting_universe_uid)
    if accounting_universe is None:
        raise HTTPNotFound
    
    retval = []
    for total_account in accounting_universe.total_accounts:
        for aggregate_account in total_account.aggregate_accounts:
            for simple_account in aggregate_account.accounts:
                account = {
                    'uid': simple_account.uid,
                    'name': simple_account.name,
                    'description': simple_account.description,
                    'parent': simple_account.parent_account.uid,
                }
                retval.append(account)
            account = {
                'uid': aggregate_account.uid,
                'name': '* ' + aggregate_account.name,
                'description': aggregate_account.description,
                'parent': aggregate_account.parent_account.uid,
            }
            retval.append(account)
        account = {
            'uid': total_account.uid,
            'name': '** ' + total_account.name,
            'description': total_account.description,
            'parent': None,
        }
        retval.append(account)
    return retval


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
    isodate = request.params.get('date', date.today().isoformat())
    ref_date = date(*map(int, isodate.split('-')))
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
            'item_class_uid': itemset.item_class.uid,
            'item_count': itemset.balance(ref_date),
        } for itemset in itemsets
    ]
    return retval


@view_config(route_name='itemset_transactions_json', renderer='json', request_method='GET')
@extjs_rest
def itemset_transactions_json(request, page=1, start=0, limit=25):
    user_uid = request.matchdict['user_uid']
    book_uid = request.matchdict['book_uid']
    itemset_uid = request.matchdict['itemset_uid']
    isodate = request.params.get('date', date.today().isoformat())
    # ref_date = date(*map(int, isodate.split('-')))
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    books = user.books.filter('uid =', book_uid).fetch(2)
    if len(books) != 1:
        raise HTTPNotFound
    itemsets = books[0].inventory.filter('uid =', itemset_uid).fetch(2)
    if len(itemsets) != 1:
        raise HTTPNotFound
    transactions = itemsets[0].inventory_transactions.fetch(min(limit, book_itemsets_limit), offset=start)
    retval = [
        {
            'uid': transaction.start_date.isoformat(),
            'name': transaction.end_date.isoformat(), 
            'accounting_universe_uid': transaction.name,
            'inventory_count': transaction.amount,
        } for transaction in transactions
    ]
    return retval
