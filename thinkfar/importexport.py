
from .accounting import AccountingTreeRoot, TotalAccount, AggregateAccount, Account
from .inventory import User

__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


def update_or_insert_batch(klasses, batch, key_prefix='', **kwds):
    assert len(klasses) > 0
    for keys in batch:
        children = keys.pop('children', [])
        key_name = '%s/%s' % (key_prefix, keys['uid'])
        keys.update(kwds)
        instance = klasses[0].get_by_key_name(key_name)
        if instance is None:
            instance = klasses[0](key_name=key_name, **keys)
        else:
            instance.setattrs(**keys)
        instance.put()
        if len(children) > 0:
            update_or_insert_batch(klasses[1:], children, key_prefix=key_prefix, parent_account=instance)


def load_accounting_tree(uid, name, tree):
    root = AccountingTreeRoot.get_by_key_name(uid)
    if root is None:
        root = AccountingTreeRoot(key_name=uid, uid=uid, name=name)
    else:
        root.setattrs(uid=uid, name=name)
    root.put()
    update_or_insert_batch([TotalAccount, AggregateAccount, Account], tree, key_prefix=uid, parent_account=root)


def load_items(klass, items):
    for keys in items:
        key_name = keys['uid']
        item = klass.get_by_key_name(key_name)
        if item is None:
            item = klass(key_name=key_name, **keys)
        else:
            item.setattrs(**keys)
        item.put()
