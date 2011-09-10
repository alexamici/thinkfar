
from .accounting import TotalAccount, AggregateAccount, Account
from .inventory import AccountingUniverse, ItemClass

__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


def update_or_insert_batch(klasses, items, key_prefix='', **kargs):
    assert len(klasses) > 0
    for keys in items:
        children = keys.pop('children', [])
        key_name = '%s/%s' % (key_prefix, keys['uid'])
        keys.update(kargs)
        item = klasses[0].get_by_key_name(key_name)
        if item is None:
            item = klasses[0](key_name=key_name, **keys)
        else:
            for key, value in keys.items():
                setattr(item, key, value)
        item.put()
        if len(children) > 0:
            update_or_insert_batch(klasses[1:], children, key_prefix=key_prefix, parent_account=item)


def load_accounting_tree(root, accounting_tree):
    update_or_insert_batch([TotalAccount, AggregateAccount, Account], accounting_tree, key_prefix=root.uid, accounting_universe=root)


def load_items(klass, items, **kargs):
    for keys in items:
        key_name = keys['uid']
        keys.update(kargs)
        item = klass.get_by_key_name(key_name)
        if item is None:
            item = klass(key_name=key_name, **keys)
        else:
            for key, value in keys.items():
           	    setattr(item, key, value)
        item.put()
