
from pyramid.config import Configurator


def app(global_config=None, **settings):
    """ This function returns a WSGI application.

    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    config = Configurator(settings=settings)
    config.begin()
    config.add_route('accounting_trees', '/accounting_trees/{uuid}')
    config.scan()
    config.end()
    return config.make_wsgi_app()
