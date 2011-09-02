
from simplejson import dumps

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from .accounting import AccountingTreeRoot
from .inventory import User


__copyright__ = 'Copyright (c) 2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


@view_config(request_method='GET')
def root_view(request):
	return Response('<h1>Think-Far!</h1>')

@view_config(route_name='accounting_trees', request_method='GET')
def accounting_trees(request):
	tree_uid = request.matchdict['tree_uid']
	tree = AccountingTreeRoot.get_by_key_name(tree_uid)
	if tree is None:
		raise HTTPNotFound
	return Response(dumps((tree.uid, tree.name)))

@view_config(route_name='users', request_method='GET')
def users(request):
	user_uid = request.matchdict['user_uid']
	user = User.get_by_key_name(user_uid)
	if user is None:
		raise HTTPNotFound
	return Response(dumps((user.uid, user.principal.email(), user.principal.user_id())))
