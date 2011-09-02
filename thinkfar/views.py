
from simplejson import dumps

from pyramid.response import Response
from pyramid.view import view_config

from .accounting import AccountingTreeRoot

@view_config(request_method='GET')
def root_view(request):
	return Response('<h1>Think-Far!</h1>')

@view_config(route_name='accounting_trees', request_method='GET')
def accounting_trees(request):
	uuid = request.matchdict['uuid']
	tree = AccountingTreeRoot.get_by_key_name(uuid)
	return Response(dumps((tree.uuid, tree.name)))
