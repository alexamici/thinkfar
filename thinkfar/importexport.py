
__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


def load_items(klass, items, key_prefix='', children_classes=[], **kargs):
    for keys in items:
        children = keys.pop('children', [])
        key_name = '%s%s' % (key_prefix, keys['uid'])
        keys.update(kargs)
        item = klass.get_by_key_name(key_name)
        if item is None:
            item = klass(key_name=key_name, **keys)
        else:
            for key, value in keys.items():
                setattr(item, key, value)
        item.put()
        if len(children) > 0:
            load_items(children_classes[0], children, key_prefix=key_prefix, parent_account=item, children_classes=children_classes[1:])
