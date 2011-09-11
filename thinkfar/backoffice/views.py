

from pyramid.response import Response
from pyramid.view import view_config

from .accounting import init_gifi_accounting_universe
from .inventory import init_datastore


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


@view_config(name='init_gifi_accounting_universe', request_method='GET')
def init_gifi_accounting_universe_view(request):
    init_gifi_accounting_universe()
    return Response('Ok')

@view_config(name='init_datastore', request_method='GET')
def init_datastore_view(request):
    init_datastore()
    return Response('Ok')

