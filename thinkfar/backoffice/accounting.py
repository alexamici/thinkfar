
from ..accounting import TotalAccount, AggregateAccount, Account, ItemClass, TransactionTemplate, load_accounting_tree
from ..importexport import load_items
from ..inventory import AccountingUniverse


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


gifi_item_classes = [
    ItemClass, [
        {'uid': '1001', 'name': 'Legal Currency'},
        {'uid': '1002', 'name': 'Bank Account', 'description': 'Denominated in the main legal currency'},
        {'uid': '1126', 'name': 'Commodity'},
        {'uid': '1600', 'name': 'Land'},
        {'uid': '1680', 'name': 'Building'},
        {'uid': '1740', 'name': 'Vehicle', 'children': [
            TransactionTemplate, [
                {'uid': 'buy', 'allowed_kargs': ['gross_price_paid', 'taxes_paid', 'fees_paid', 'resell_value'],
                    'target_accounts_uids': ['GIFI/1002', 'GIFI/9990', 'GIFI/8870', 'GIFI/1740']},
                {'uid': 'sell', 'allowed_kargs': ['gross_price_paid', 'taxes_paid', 'fees_paid', 'resell_value'],
                    'target_accounts_uids': ['GIFI/1002', 'GIFI/9990', 'GIFI/8870', 'GIFI/1740']},
            ]
        ]},
        {'uid': '2707', 'name': 'Credit Card'},
        {'uid': '2010', 'name': 'Job'},
        {'uid': '3500', 'name': 'Shares'},
        {'uid': '3141', 'name': 'Mortgage'},
    ],
]

# GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf
gifi_accounting_tree = [
    TotalAccount, [
        {'uid': '2599', 'name': 'Total assets', 'is_asset': True, 'children': [
            AggregateAccount, [
                {'uid': '1599', 'name': 'Total current assets', 'children': [
                    Account, [
                        {'uid': '1001', 'name': 'Cash'},
                        {'uid': '1002', 'name': 'Deposits in local banks and institutions'},
                        {'uid': '1007', 'name': 'Other cash like instruments'},
                        {'uid': '1126', 'name': 'Raw materials'},
                    ],
                ]},
                {'uid': '2008', 'name': 'Total tangible capital assets', 'children': [
                    Account, [
                        {'uid': '1600', 'name': 'Land'},
                        {'uid': '1680', 'name': 'Buildings'},
                        {'uid': '1740', 'name': 'Machinery, equipment, furniture, and fixtures'},
                    ],
                ]},
                {'uid': '2178', 'name': 'Total intangible capital assets', 'children': [
                    Account, [
                        {'uid': '2010', 'name': 'Intangible assets'},
                        {'uid': '2070', 'name': 'Resource rights'},
                    ],
                ]},
            ],
        ]},
        {'uid': '3640', 'name': 'Total liabilities and shareholder equity', 'is_liability': True, 'children': [
            AggregateAccount, [
                {'uid': '3499', 'name': 'Total liabilities', 'children': [
                    Account, [
                        {'uid': '2600', 'name': 'Bank overdraft'},
                        {'uid': '2707', 'name': 'Credit card loans'},
                        {'uid': '3141', 'name': 'Mortgages'},
                        {'uid': '3450', 'name': 'Long-term liabilities'},
                    ],
                ]},
                {'uid': '3620', 'name': 'Total equity', 'children': [
                    Account, [
                        {'uid': '3500', 'name': 'Common shares'},
                    ],
                ]},
            ],
        ]},
        {'uid': '8299', 'name': 'Total revenue', 'is_revenue': True, 'children': [
            AggregateAccount, [
                {'uid': '8089', 'name': 'Total sales of goods and services', 'children': [
                    Account, [
                        {'uid': '8000', 'name': 'Trade sales of goods and services'},
                    ],
                ]},
                {'uid': '8140', 'name': 'Total rental revenue', 'children': [
                    Account, [
                        {'uid': '8141', 'name': 'Real estate rental revenue'},
                    ],
                ]},
                {'uid': '8210', 'name': 'Total Realized gains/losses on disposal of assets', 'children': [
                    Account, [
                        {'uid': '8211', 'name': 'Realized gains/losses on sale of investments'},
                        {'uid': '8212', 'name': 'Realized gains/losses on sale of resource properties'},
                    ],
                ]},
            ],
        ]},
        {'uid': '9368', 'name': 'Total expenses', 'is_expense': True, 'children': [
            AggregateAccount, [
                {'uid': '9367', 'name': 'Total operating expenses', 'children': [
                    Account, [
                        {'uid': '8690', 'name': 'Insurance'},
                        {'uid': '8710', 'name': 'Interest and bank charges'},
                        {'uid': '8764', 'name': 'Government fees'},
                        {'uid': '8870', 'name': 'Transfer fees'},
                        {'uid': '8961', 'name': 'Repairs and maintenance - buildings'},
                        {'uid': '8962', 'name': 'Repairs and maintenance - vehicles'},
                        {'uid': '9180', 'name': 'Property taxes'},
                        {'uid': '9130', 'name': 'Supplies'},
                        {'uid': '9990', 'name': 'Current income taxes'},
                    ],
                ]},
            ],
        ]},
    ]
]


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
    load_items(gifi_item_classes, key_prefix='GIFI/', accounting_universe=root,
        parent_key='item_class')
    load_accounting_tree(root, gifi_accounting_tree)
