
from json import dumps

from pyramid.response import Response
from pyramid.view import view_config

from .accounting import AccountingTreeRoot

@view_config(route_name='accounting_trees', request_method='GET')
def accounting_trees(request):
	uuid = request.matchdict['uuid']
	return Response(dumps(tree))
