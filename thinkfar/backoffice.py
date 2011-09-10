
from google.appengine.api.users import User as GAE_User

from pyramid.response import Response
from pyramid.view import view_config

from .importexport import load_items, load_accounting_tree
from .inventory import User, Currency, AccountingUniverse, ItemClass


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

init_accounting_universes = (
    {'uid': 'GIFI', 'name': 'General Index of Financial Information',
        'description': 'GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf'},
)

gifi_item_classes = (
    {'uid': 'GIFI-1001', 'name': 'Legal Currency'},
    {'uid': 'GIFI-1002', 'name': 'Bank Account', 'description': 'Denominated in the main legal currency'},
    {'uid': 'GIFI-1126', 'name': 'Commodity'},
    {'uid': 'GIFI-1600', 'name': 'Land'},
    {'uid': 'GIFI-1680', 'name': 'Building'},
    {'uid': 'GIFI-1740', 'name': 'Vehicle'},
    {'uid': 'GIFI-2707', 'name': 'Credit Card'},
    {'uid': 'GIFI-2010', 'name': 'Job'},
    {'uid': 'GIFI-3500', 'name': 'Shares'},
    {'uid': 'GIFI-3141', 'name': 'Mortgage'},
)

# GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf
gifi_accounting_tree = (
    {'uid': '2599', 'name': 'Total assets', 'is_asset': True, 'children': (
        {'uid': '1599', 'name': 'Total current assets', 'children': (
            {'uid': '1001', 'name': 'Cash'},
            {'uid': '1002', 'name': 'Deposits in local banks and institutions'},
            {'uid': '1007', 'name': 'Other cash like instruments'},
            {'uid': '1126', 'name': 'Raw materials'},
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


init_users = (
    {'uid': 'alexamici', 'principal': GAE_User('alexamici@gmail.com'), 'default_currency': 'EUR'},
)


@view_config(name='load_gifi_accounting_universe', request_method='GET')
def load_gifi_accounting_universe(request):
    root = AccountingUniverse.get_by_key_name('GIFI')
    load_accounting_tree(root, gifi_accounting_tree)
    load_items(ItemClass, gifi_item_classes, accounting_universe=root)
    return Response('Ok')

@view_config(name='load_init', request_method='GET')
def load_init(request):
    load_items(Currency, init_currencies)
    load_items(User, init_users)
    load_items(AccountingUniverse, init_accounting_universes)
    return Response('Ok')

