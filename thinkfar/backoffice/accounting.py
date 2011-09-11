
from ..accounting import load_accounting_tree
from ..inventory import AccountingUniverse


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


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
            {'uid': '8690', 'name': 'Insurance'},
            {'uid': '8710', 'name': 'Interest and bank charges'},
            {'uid': '8764', 'name': 'Government fees'},
            {'uid': '8870', 'name': 'Transfer fees'},
            {'uid': '8961', 'name': 'Repairs and maintenance - buildings'},
            {'uid': '8962', 'name': 'Repairs and maintenance - vehicles'},
            {'uid': '9180', 'name': 'Property taxes'},
            {'uid': '9130', 'name': 'Supplies'},
            {'uid': '9990', 'name': 'Current income taxes'},
        )},
    )},
)


#'transaction_definitions': [
#    'buy:9180,8870,1600',
#    'sell:9180,8870,1600',
#    'costs:8870,8961',
#    'revenues:8141,9990']
#'transaction_definitions': [
#    'buy:9180,8870,1740',
#    'sell:9180,8870,1600',
#    'costs:8690,8961']

def init_gifi_accounting_universe():
    root = AccountingUniverse.get_by_key_name('GIFI')
    load_accounting_tree(root, gifi_accounting_tree)
