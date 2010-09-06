
from webob import Response
from repoze.bfg.configuration import Configurator

from google.appengine.ext.webapp import RequestHandler, WSGIApplication
from google.appengine.ext.webapp.util import login_required


class RootHandler(RequestHandler):

    @login_required
    def get(self):
        """Handles GET."""

        # The request object as well as the response object must provide a
        # special marker interface to be adaptable.
        zope.interface.directlyProvides(self.request, interfaces.IRequest)
        zope.interface.directlyProvides(self.response, interfaces.IResponse)

        # Try to get a named multi adapter for a context object and the
        # request.
        page = zope.component.getMultiAdapter((None, self.request),
                                              interfaces.IPage, "index.html")

        # And write its rendered output to the response object.
        self.response.out.write(page.render())


def application():
    """Returns WSGI application object."""

    config = Configurator()
    config.begin()
    config.load_zcml()
    config.scan()
    config.end()
    app = config.make_wsgi_app()

    # We register some request handlers for our application.
    # app = WSGIApplication([
    #    (r'/', RootHandler),
    # ], debug=True)

    return app

