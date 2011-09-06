
from google.appengine.api.users import User as GAE_User

from pyramid.response import Response
from pyramid.view import view_config

from .importexport import load_items, load_accounting_tree
from .inventory import User, Currency


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


# ISO 4217 - http://en.wikipedia.org/wiki/ISO_4217
init_currencies =(
    {'uid': 'XAU', 'name': 'Gold (one troy ounce)'},
    {'uid': 'XAG', 'name': 'Silver (one troy ounce)'},
    {'uid': 'USD', 'name': 'United States dollar'},
    {'uid': 'EUR', 'name': 'Euro'},
    {'uid': 'GBP', 'name': 'Pound sterling'},
    {'uid': 'JPY', 'name': 'Japanese yen'},
)

# GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf
gifi_accounting_tree = (
    {'uid': '2599', 'name': 'Total assets', 'is_asset': True, 'children': (
        {'uid': '1599', 'name': 'Total current assets', 'children': (
            {'uid': '1001', 'name': 'Cash'},
            {'uid': '1002', 'name': 'Deposits in local banks and institutions'},
            {'uid': '1007', 'name': 'Other cash like instruments'},
            {'uid': '1122', 'name': 'Inventory parts and supplies'},
        )},
        {'uid': '2008', 'name': 'Total tangible capital assets', 'children': (
            {'uid': '1600', 'name': 'Land'},
            {'uid': '1680', 'name': 'Buildings'},
            {'uid': '1740', 'name': 'Machinery, equipment, furniture, and fixtures'},
        )},
        {'uid': '2178', 'name': 'Total intangible capital assets', 'children': (
            {'uid': '2010', 'name': 'Intangible assets'},
            {'uid': '2070', 'name': 'Resource rights'},
        )},
    )},
    {'uid': '3640', 'name': 'Total liabilities and shareholder equity', 'is_liability': True, 'children': (
        {'uid': '3499', 'name': 'Total liabilities', 'children': (
            {'uid': '2600', 'name': 'Bank overdraft'},
            {'uid': '2707', 'name': 'Credit card loans'},
            {'uid': '3141', 'name': 'Mortgages'},
            {'uid': '3450', 'name': 'Long-term liabilities'},
        )},
        {'uid': '3620', 'name': 'Total equity', 'children': (
            {'uid': '3500', 'name': 'Common shares'},
        )},
    )},
    {'uid': '8299', 'name': 'Total revenue', 'is_revenue': True, 'children': (
        {'uid': '8089', 'name': 'Total sales of goods and services', 'children': (
            {'uid': '8000', 'name': 'Trade sales of goods and services'},
        )},
        {'uid': '8140', 'name': 'Total rental revenue', 'children': (
            {'uid': '8141', 'name': 'Real estate rental revenue'},
        )},
        {'uid': '8210', 'name': 'Total Realized gains/losses on disposal of assets', 'children': (
            {'uid': '8211', 'name': 'Realized gains/losses on sale of investments'},
            {'uid': '8212', 'name': 'Realized gains/losses on sale of resource properties'},
        )},
    )},
    {'uid': '9368', 'name': 'Total expenses', 'is_expense': True, 'children': (
        {'uid': '9367', 'name': 'Total operating expenses', 'children': (
            {'uid': '8710', 'name': 'Interest and bank charges'},
            {'uid': '8764', 'name': 'Government fees'},
            {'uid': '9180', 'name': 'Property taxes'},
            {'uid': '9130', 'name': 'Supplies'},
        )},
    )},
)


init_users = [
    {'uid': 'alexamici', 'principal': GAE_User('alexamici@gmail.com'), 'default_currency': 'EUR'}
]


@view_config(name='load_gifi_accounting_tree', request_method='GET')
def load_gifi_accounting_tree(request):
    load_accounting_tree('GIFI', 'GIFI', gifi_accounting_tree)
    return Response('Ok')

@view_config(name='load_init_users', request_method='GET')
def load_init_users(request):
    for user in init_users:
        user['default_currency'] = Currency.get_by_key_name(user.get('default_currency', 'EUR'))
    load_items(User, init_users)
    return Response('Ok')

@view_config(name='load_init_currencies', request_method='GET')
def load_init_currencies(request):
    load_items(Currency, init_currencies)
    return Response('Ok')
