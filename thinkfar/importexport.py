
__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'
__version__ = '0.7-pre-alpha'


def load_items(definition, key_prefix='', parent_key='parent_account', **kargs):
    klass, items = definition
    for keys in items:
        children = keys.pop('children', [None, []])
        key_name = '%s%s' % (key_prefix, keys['uid'])
        keys.update(kargs)
        item = klass.get_by_key_name(key_name)
        if item is None:
            item = klass(key_name=key_name, **keys)
        else:
            for key, value in keys.items():
                setattr(item, key, value)
        item.put()
        if len(children[1]) > 0:
            kwargs_children = kargs.copy()
            kwargs_children.update({
                'key_prefix': key_prefix,
                parent_key: item,
            })
            load_items(children, **kwargs_children)
