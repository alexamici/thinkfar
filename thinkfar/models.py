"""
'Price is what you pay. Value is what you get.' Warren Buffett, 2008.
"""

from datetime import date

from google.appengine.api.memcache import set, get
from google.appengine.ext.db import Model, FloatProperty, StringProperty, BooleanProperty
from google.appengine.ext.db import TextProperty, DateProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty


class Root(object):
    title = u'think beyond the end of your nose'

root = Root()

def get_root(request):
    return root


class Portfolio(Model):
    """A collection of assets with an associated double-entry book"""
    
    owner = UserProperty(required=True)
    name = StringProperty(required=True, default=u'Default Portfolio')
    description = TextProperty()
    opening_transaction = ReferenceProperty(collection_name='opening_transaction_of') # one-way relation to Transaction
    default_cash_asset = ReferenceProperty(collection_name='default_cash_asset_of') # one-way relation to Asset

    @property
    def id(self):
        return self.key().id()

    def put(self):
        if self.is_saved():
            return super(Portfolio, self).put()
        super(Portfolio, self).put()
        currency = AssetModel.all().filter('name =', 'Currency').fetch(1)[0]
        usd = Asset(portfolio=self, asset_model=currency, name=u'Bank USD', identity=u'USD')
        usd.put(init_cash=True)
        self.default_cash_asset = usd
        for definition in AccountDefinition.all():
            account = Account(definition=definition, denomination=usd, asset=None)
            account.put()
        usd_balance = Account(definition=self.account_by_code('1001').definition, denomination=usd, asset=usd)
        usd_balance.put()
        gold = Asset(portfolio=self, asset_model=currency, name=u'Gold coins 1oz', identity=u'GOLD')
        gold.put()
        opening_transaction = Transaction(date=date(2000, 1, 1), description=u'Opening Balance')
        opening_transaction.put()
        self.opening_transaction = opening_transaction
        return super(Portfolio, self).put()

    def total_accounts(self):
        return [a for a in self.accounts() if a.definition.parent_account is None]

    def total_balance_sheet_accounts(self):
        return sorted([a for a in self.accounts() if a.definition.parent_account is None and a.definition.in_balance_sheet], 
            cmp=lambda x, y: int(x.definition.code) - int(y.definition.code))

    def total_income_statment_accounts(self):
        return sorted([a for a in self.accounts() if a.definition.parent_account is None and not a.definition.in_balance_sheet], 
            cmp=lambda x, y: int(x.definition.code) - int(y.definition.code))

    def accounts(self, asset=None):
        return Account.all().filter('denomination =', self.default_cash_asset).filter('asset =', asset).filter('definition !=', None)

    def leaf_accounts(self, code=None):
        all_leaf_accounts = Account.all().filter('denomination =', self.default_cash_asset).filter('asset !=', None)
        if code == None:
            return all_leaf_accounts
        else:
            return [a for a in all_leaf_accounts if a.definition.code == code]

    def all_accounts(self):
        return Account.all().filter('denomination IN', list(self.assets))

    def account_by_code(self, code, asset=None):
        accounts = [a for a in self.accounts(asset=asset) if a.definition.code == code]
        assert len(accounts) == 1, 'code: %r asset: %r accounts: %r' % (code, asset, accounts)
        return accounts[0]

    def account_by_codes(self, codes, asset=None):
        definitions = AccountDefinition.all().filter('code IN', codes)
        return Account.all().filter('denomination =', self.default_cash_asset).filter('asset =', asset).filter('definition IN', list(definitions))

    def trade_asset(self, asset, date=None, amount=1., price=None, price_account=None, description=None,
         taxes=0., fees=0.):
        '''trade an asset using default accounts
        
        if date is None the trade is added to the opening balance for the accounts'''
        if date is None:
            transaction = self.opening_transaction
            price_account = self.account_by_code('3500') # equity
        else:
            transaction = Transaction(date=date, description=description)
            transaction.put()
            price_account = price_account or self.default_cash_asset.parent_account
        transaction.add_entries(((asset.inventory, amount), (asset.parent_account, - price), (price_account, price)))
        transaction.put()

    def __repr__(self):
        return u'<%s object name=%r owner=%r>' % \
            (self.__class__.__name__, self.name, self.owner.nickname())

class AssetModel(Model):
    name = StringProperty(required=True)
    description = TextProperty()
    parent_account_code = StringProperty()

    base_instances_keys = (
        {'name': 'Currency', 'parent_account_code': '1001'},
        {'name': 'Commodity', 'parent_account_code': '1122'},
        {'name': 'Land', 'parent_account_code': '1600'},
        {'name': 'Building', 'parent_account_code': '1680'},
        {'name': 'Vehicle', 'parent_account_code': '1740'},
        {'name': 'Credit Card', 'parent_account_code': '2707'},
        {'name': 'Job', 'parent_account_code': '2010'},
        {'name': 'Mortgage', 'parent_account_code': '3141'},
    )

    @classmethod
    def get_by_name(self, name):
        return AssetModel.all().filter('name =', name).fetch(1)[0]

    def __repr__(self):
        return u'<%s object name=%r>' % \
            (self.__class__.__name__, self.name)

class Asset(Model):
    """Base asset class"""
    portfolio = ReferenceProperty(Portfolio, required=True, collection_name='assets')
    asset_model = ReferenceProperty(AssetModel, required=True)
    name = StringProperty(required=True)
    identity = StringProperty()
    long_identity = TextProperty()

    @property
    def id(self):
        return self.key().id()

    @property
    def parent_account(self):
        return self.portfolio.account_by_code(self.asset_model.parent_account_code, asset=self)

    @property
    def has_identity(self):
        return self.identity is not None

    def put(self, init_cash=False):
        if self.is_saved():
            return super(Asset, self).put()
        key = super(Asset, self).put()
        inventory = Account(definition=None, denomination=self)
        inventory.put()
        if not init_cash:
            parent_account = Account(definition=self.portfolio.account_by_code(self.asset_model.parent_account_code).definition,
                denomination=self.portfolio.default_cash_asset, asset=self)
            parent_account.put()
        return key

    def buy(self, amount=1., price=None, **keys):
        if price == None:
            price = amount
        self.portfolio.trade_asset(self, amount=amount, price=-price, **keys)

    def sell(self, date, amount=1., value=None, **keys):
        if value == None:
            value = amount
        self.portfolio.trade_asset(self, date=date, amount=-amount, price=value, **keys)

    def reconcile(self, date, descpription=None, code='8212'):
        parent_account_balance = self.parent_account.balance(date)
        if parent_account_balance == 0 or self.inventory.balance(date) != 0.:
            return
        profit_loss = Transaction(date=date, descpription=descpription)
        profit_loss.put()
        profit_loss_account = self.portfolio.account_by_code(code)
        profit_loss.add_entries(((self.parent_account, - parent_account_balance), (profit_loss_account, parent_account_balance)))

    @property
    def inventory(self):
        for a in self.denomination_accounts:
            if a.definition is None:
                return a

    def __repr__(self):
        if self.has_identity:
            identification = u'identity=%r' % self.identity
        else:
            identification = u''
        return u'<%s object name=%r %s portfolio=%r owner=%r>' % \
            (self.__class__.__name__, self.name, identification,
                self.portfolio.name, self.portfolio.owner.nickname())

# GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf
class AccountDefinition(Model):
    code = StringProperty(required=True)
    name = StringProperty(required=True)
    in_balance_sheet = BooleanProperty(default=True)
    description = TextProperty()
    parent_account = SelfReferenceProperty(collection_name='children_accounts')

    base_instances_keys = (
        {'code': '2599', 'name': 'Total assets', 'children': (
            {'code': '1599', 'name': 'Total current assets', 'children': (
                {'code': '1001', 'name': 'Cash'},
                {'code': '1122', 'name': 'Inventory parts and supplies'},
            )},
            {'code': '2008', 'name': 'Total tangible capital assets', 'children': (
                {'code': '1600', 'name': 'Land'},
                {'code': '1680', 'name': 'Buildings'},
                {'code': '1740', 'name': 'Machinery, equipment, furniture, and fixtures'},
            )},
            {'code': '2178', 'name': 'Total intangible capital assets', 'children': (
                {'code': '2010', 'name': 'Intangible assets'},
            )},
            {'code': '2589', 'name': 'Total long-term assets'},
        )},
        {'code': '3640', 'name': 'Total liabilities and shareholder equity', 'children': (
            {'code': '3499', 'name': 'Total liabilities', 'children': (
                {'code': '2600', 'name': 'Bank overdraft'},
                {'code': '2707', 'name': 'Credit card loans'},
                {'code': '3141', 'name': 'Mortgages'},
            )},
            {'code': '3620', 'name': 'Total equity', 'children': (
                {'code': '3500', 'name': 'Common shares'},
            )},
        )},
        {'code': '8299', 'name': 'Total revenue', 'in_balance_sheet': False, 'children': (
            {'code': '8089', 'name': 'Total sales of goods and services', 'children': (
                {'code': '8000', 'name': 'Trade sales of goods and services'},
            )},
            {'code': '8140', 'name': 'Total rental revenue', 'children': (
                {'code': '8141', 'name': 'Real estate rental revenue'},
            )},
            {'code': '8210', 'name': 'Total Realized gains/losses on disposal of assets', 'children': (
                {'code': '8211', 'name': 'Realized gains/losses on sale of investments'},
                {'code': '8212', 'name': 'Realized gains/losses on sale of resource properties'},
            )},
        )},
        {'code': '9368', 'name': 'Total expenses', 'in_balance_sheet': False, 'children': (
            {'code': '9367', 'name': 'Total operating expenses', 'children': (
                {'code': '8710', 'name': 'Interest and bank charges'},
            )},
        )},
    )

    @property
    def id(self):
        return self.key().id()

class Account(Model):
    """A double-entry or inventory account belonging to a portfolio
    
    Double-entry accounts have a definition
    Asset accounts have an asset
    Inventory accounts have no definition and no asset"""

    definition = ReferenceProperty(AccountDefinition, collection_name='accounts')
    denomination = ReferenceProperty(Asset, required=True, collection_name='denomination_accounts')
    asset = ReferenceProperty(Asset, default=None, collection_name='accounts')

    @property
    def id(self):
        return self.key().id()

    @property
    def children_accounts(self):
        if self.is_inventory or self.is_asset_account:
            return []
        cached_children_accounts = get('account-%d-children_accounts' % self.id)
        if cached_children_accounts is not None:
            return cached_children_accounts
        codes = [am.code for am in self.definition.children_accounts]
        children_accounts = list(self.denomination.portfolio.account_by_codes(codes))
        children_accounts += self.denomination.portfolio.leaf_accounts(self.definition.code)
        set('account-%d-children_accounts' % self.id, children_accounts, time=3600)
        return children_accounts

    @property
    def is_inventory(self):
        return self.definition is None and self.asset is None

    @property
    def is_asset_account(self):
        return self.asset is not None

    def transactions(self):
        return [te.transaction for te in self.transaction_entries]

    def balance(self, date):
        children_balance = sum(a.balance(date) for a in self.children_accounts)
        return 0. + children_balance + sum(te.amount for te in self.transaction_entries if te.transaction.date <= date)

    def total_credit(self, date):
        return sum(te.amount for te in self.transaction_entries if te.transaction.date <= date and te.amount > 0.)
    
    def total_debit(self, date):
        return sum(te.amount for te in self.transaction_entries if te.transaction.date <= date and te.amount < 0.)

    def __repr__(self):
        if self.definition is None:
            name = self.denomination.name
            in_balance_sheet = True
            code = None
        else:
            name = self.definition.name
            in_balance_sheet = self.definition.in_balance_sheet
            code = self.definition.code
        return u'<%s object denomination=%r name=%r code=%r asset=%r in_balance_sheet=%r>' % \
            (self.__class__.__name__, self.denomination.identity, name, code, self.asset, in_balance_sheet)

class Transaction(Model):
    """An event in the double-entry book
    
    if date is None it is a transaction template, not an actual transaction"""

    date = DateProperty()
    description = TextProperty()

    @property
    def id(self):
        return self.key().id()

    def is_balanced(self):
        # transaction_entities belonging to inventory accounts are not balanced
        balanced_transaction_entities = filter(lambda te: te.account.description is not None, self.transaction_entries)
        balanced_denominations = set(te.account.denomination for te in balanced_transaction_entities)
        for d in balanced_denominations:
            balance = sum(te.amount for te in balanced_transaction_entities if te.account.denomination is d)
            if balance:
                return False
        return True

    def add_entries(self, entries):
        balance = sum(te.amount for te in self.transaction_entries) + sum(e[1] for e in entries)
        if balance is not 0.:
            pass
            # raise ValueError('Unbalanced transaction: %r' % balance)
        for e in entries:
            te = TransactionEntry(transaction=self, account=e[0], amount=e[1])
            te.put()

class TransactionEntry(Model):
    transaction = ReferenceProperty(Transaction, required=True, collection_name='transaction_entries')
    account = ReferenceProperty(Account, required=True, collection_name='transaction_entries')
    amount = FloatProperty(required=True)


# OBSOLETE

class Trade(Model):
    """A representation of a financial/commercial trade that includes the spread
    between buyer_price and seller_value due to taxes, fees, etc.

    The basic idea is to separate total price paid by the seller in the
    transaction from what the seller actually receives."""
    pass
