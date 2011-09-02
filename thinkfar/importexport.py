
from .accounting import AccountingTreeRoot, TotalAccount, AggregateAccount, Account


# GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf
gifi_accounting_tree = (
    {'uuid': '2599', 'name': 'Total assets', 'is_asset': True, 'children': (
        {'uuid': '1599', 'name': 'Total current assets', 'children': (
            {'uuid': '1001', 'name': 'Cash'},
            {'uuid': '1002', 'name': 'Deposits in local banks and institutions'},
            {'uuid': '1007', 'name': 'Other cash like instruments'},
            {'uuid': '1122', 'name': 'Inventory parts and supplies'},
        )},
        {'uuid': '2008', 'name': 'Total tangible capital assets', 'children': (
            {'uuid': '1600', 'name': 'Land'},
            {'uuid': '1680', 'name': 'Buildings'},
            {'uuid': '1740', 'name': 'Machinery, equipment, furniture, and fixtures'},
        )},
        {'uuid': '2178', 'name': 'Total intangible capital assets', 'children': (
            {'uuid': '2010', 'name': 'Intangible assets'},
            {'uuid': '2070', 'name': 'Resource rights'},
        )},
    )},
    {'uuid': '3640', 'name': 'Total liabilities and shareholder equity', 'is_liability': True, 'children': (
        {'uuid': '3499', 'name': 'Total liabilities', 'children': (
            {'uuid': '2600', 'name': 'Bank overdraft'},
            {'uuid': '2707', 'name': 'Credit card loans'},
            {'uuid': '3141', 'name': 'Mortgages'},
            {'uuid': '3450', 'name': 'Long-term liabilities'},
        )},
        {'uuid': '3620', 'name': 'Total equity', 'children': (
            {'uuid': '3500', 'name': 'Common shares'},
        )},
    )},
    {'uuid': '8299', 'name': 'Total revenue', 'is_revenue': True, 'children': (
        {'uuid': '8089', 'name': 'Total sales of goods and services', 'children': (
            {'uuid': '8000', 'name': 'Trade sales of goods and services'},
        )},
        {'uuid': '8140', 'name': 'Total rental revenue', 'children': (
            {'uuid': '8141', 'name': 'Real estate rental revenue'},
        )},
        {'uuid': '8210', 'name': 'Total Realized gains/losses on disposal of assets', 'children': (
            {'uuid': '8211', 'name': 'Realized gains/losses on sale of investments'},
            {'uuid': '8212', 'name': 'Realized gains/losses on sale of resource properties'},
        )},
    )},
    {'uuid': '9368', 'name': 'Total expenses', 'is_expense': True, 'children': (
        {'uuid': '9367', 'name': 'Total operating expenses', 'children': (
            {'uuid': '8710', 'name': 'Interest and bank charges'},
            {'uuid': '8764', 'name': 'Government fees'},
            {'uuid': '9180', 'name': 'Property taxes'},
            {'uuid': '9130', 'name': 'Supplies'},
        )},
    )},
)


def load_accounting_tree(uuid, name, tree):
    root = AccountingTreeRoot(uuid=uuid, name=name, key_name=uuid)
    root.put()
    for total_keys in tree:
        aggregate_children = total_keys.pop('children', [])
        total = TotalAccount(parent_account=root, **total_keys)
        total.put()
        for aggregate_keys in aggregate_children:
            children = aggregate_keys.pop('children', [])
            aggregate = AggregateAccount(parent_account=total, **aggregate_keys)
            aggregate.put()
            for account_keys in children:
                account = Account(parent_account=aggregate, **account_keys)
                account.put()
