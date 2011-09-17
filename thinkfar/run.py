
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
    config.add_route('accounting_universe_index_html', '/u/{accounting_universe_uid}')
    config.add_route('book_index_html', '/{user_uid}/b/{book_uid}')
    config.add_route('user_index_html', '/{user_uid}')
    config.scan()
    config.end()
    return config.make_wsgi_app()
