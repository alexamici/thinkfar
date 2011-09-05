
from pyramid.config import Configurator


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


def app(global_config=None, **settings):
    """ This function returns a WSGI application.

    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    config = Configurator(settings=settings)
    config.begin()
    config.add_route('accounting_tree_view', '/accounting_trees/{tree_uid}.html')
    config.add_route('accounting_tree_rest', '/accounting_trees/{tree_uid}')
    config.add_route('user_rest', '/users/{user_uid}')
    config.add_route('scenario_rest', '/users/{user_uid}/scenarios/{scenario_uid}')
    config.scan()
    config.end()
    return config.make_wsgi_app()
