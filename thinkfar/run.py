from pyramid.config import Configurator
# from thinkfar.models import get_root

def app(global_config=None, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    config = Configurator(settings=settings)
    config.begin()
    config.scan()
    config.end()
    return config.make_wsgi_app()
