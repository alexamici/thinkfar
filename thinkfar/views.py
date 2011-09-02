
from simplejson import dumps

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from .accounting import AccountingTreeRoot


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


@view_config(request_method='GET')
def root_view(request):
	return Response('<h1>Think-Far!</h1>')

@view_config(route_name='accounting_trees', request_method='GET')
def accounting_trees(request):
	uid = request.matchdict['uid']
	tree = AccountingTreeRoot.get_by_key_name(uid)
	if tree is None:
		raise HTTPNotFound
	return Response(dumps((tree.uid, tree.name)))
