
from google.appengine.api.users import User as GAE_User

from ..importexport import load_items
from ..inventory import User, Currency, AccountingUniverse, ItemClass


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

init_users = (
    {'uid': 'alexamici', 'principal': GAE_User('alexamici@gmail.com'), 'default_currency': 'EUR'},
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


def init_datastore():
    load_items(Currency, init_currencies)
    load_items(User, init_users)
    load_items(AccountingUniverse, init_accounting_universes)
    root = AccountingUniverse.get_by_key_name('GIFI')
    load_items(ItemClass, gifi_item_classes, accounting_universe=root)
