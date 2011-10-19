
from webapp2 import WSGIApplication, RequestHandler


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


class Test(RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp2 World!')

routes = [
    (r'/', 'thinkfar.rest.AccountsJSON'),
]

config = {}

app = WSGIApplication(routes=routes, debug=True, config=config)

def main():
    app.run()

if __name__ == '__main__':
    main()

#    config.add_static_view(name='s', path='templates/static')

#    config.add_route('accounting_universe_index_html', '/u/{accounting_universe_uid}')
#    config.add_route('accounts_json', '/u/{accounting_universe_uid}/a.json')

#    config.add_route('itemset_transactions_json', '/{user_uid}/b/{book_uid}/i/{itemset_uid}/t.json')
#    config.add_route('itemset_html', '/{user_uid}/b/{book_uid}/i/{itemset_uid}')
#    config.add_route('inventory_json', '/{user_uid}/b/{book_uid}/i.json')
#    config.add_route('book_index_html', '/{user_uid}/b/{book_uid}')
#    config.add_route('books_json', '/{user_uid}/b.json')
#    config.add_route('user_index_html', '/{user_uid}')

