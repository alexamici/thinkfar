
from os.path import join, dirname
from simplejson import dumps

from google.appengine.api.users import get_current_user, create_login_url, create_logout_url

from webapp2 import RequestHandler
from chameleon import PageTemplateLoader


# dummy migration helpers
def view_config(*args, **keys):
    return lambda x: None
HTTPNotFound = ValueError

from .inventory import User, AccountingUniverse


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.0'


# default chamaleon templates folder
templates = PageTemplateLoader(join(dirname(__file__), "templates"))


def common_template(view):
    def wrapped_view(self):
        current_user = get_current_user()
        init_namespace = {
            'current_user': current_user,
            'loggedin_url': current_user and create_logout_url('/') or create_login_url('/'),
            'loggedin_label': current_user and ('Log out %s' % current_user.nickname()) or 'Log in',
            'title': 'thinkfar',
            'main': templates['main.pt'],
            'request': self.request,
        }
        return view(self, init_namespace)    
    return wrapped_view


class RootIndexHtml(RequestHandler):
    template_name = 'main.pt'

    @common_template
    def get(self, init_namespace):
        template = templates[self.template_name]
        self.response.out.write(template(**init_namespace))


@view_config(route_name='accounting_universe_index_html', request_method='GET', renderer='templates/container.pt')
@common_template
def accounting_universe_index_html(request, init_namespace):
    accounting_universe_uid = request.matchdict['accounting_universe_uid']
    accounting_universe = AccountingUniverse.get_by_key_name(accounting_universe_uid)
    if accounting_universe is None:
        raise HTTPNotFound
    namespace = init_namespace.copy()
    fields = ['uid', 'name', 'description', 'parent']
    namespace.update({
        'container': accounting_universe, 
        'item_fields': dumps([{'name': n, 'type': 'string'} for n in fields]),
        'items_url': '/u/%s/a.json' % accounting_universe_uid,
        'items_title': 'Accounts',
        'item_columns': dumps([{'header': n.capitalize(), 'dataIndex': n} for n in fields]),
    })
    return namespace


@view_config(route_name='book_index_html', request_method='GET', renderer='templates/container.pt')
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
    fields = ['uid', 'name', 'item_class_uid', 'item_count']
    item_fields = [{'name': n, 'type': 'string'} for n in fields]
    item_fields[3]['type'] = 'int'
    namespace.update({
        'container': user,
        'item_fields': dumps(item_fields),
        'items_url': '/%s/b/%s/i.json' % (user_uid, book_uid),
        'items_title': 'Inventory',
        'item_columns': dumps([{'header': n.capitalize(), 'dataIndex': n} for n in fields]),
    })
    return namespace


@view_config(route_name='user_index_html', request_method='GET', renderer='templates/container.pt')
@common_template
def user_index_html(request, init_namespace):
    user_uid = request.matchdict['user_uid']
    user = User.get_by_key_name(user_uid)
    if user is None:
        raise HTTPNotFound
    namespace = init_namespace.copy()
    fields = ['uid', 'name', 'accounting_universe_uid', 'inventory_count']
    item_fields = [{'name': n, 'type': 'string'} for n in fields]
    item_fields[3]['type'] = 'int'
    namespace.update({
        'container': user,
        'item_fields': dumps(item_fields),
        'items_url': '/%s/b.json' % user_uid,
        'items_title': 'Accounting Books',
        'item_columns': dumps([{'header': n.capitalize(), 'dataIndex': n} for n in fields]),
    })
    return namespace
