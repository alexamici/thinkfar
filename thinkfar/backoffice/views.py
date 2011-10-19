

from webapp2 import Response

from .accounting import init_gifi_accounting_universe
from .inventory import init_datastore
from .sampledata import init_sampledata


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


def init_datastore_view(request):
    init_datastore()
    init_gifi_accounting_universe()
    return Response('Ok')

def init_sampledata_view(request):
    init_sampledata()
    return Response('Ok')