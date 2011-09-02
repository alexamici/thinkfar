
from pyramid.response import Response
from pyramid.view import view_config

from .importexport import load_accounting_tree, gifi_accounting_tree

@view_config(name='load_gifi_accounting_tree', request_method='GET')
def load_gifi_accounting_tree(request):
    load_accounting_tree('GIFI', 'GIFI', gifi_accounting_tree)
    return Response('Hello')
