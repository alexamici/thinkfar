from pyramid.config import Configurator
# from thinkfar.models import get_root

def app(global_config=None, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    config = Configurator(root_factory=None, settings=settings)
    config.begin()
    # config.scan()
    # config.load_zcml(zcml_file)
    config.end()
    return config.make_wsgi_app()
