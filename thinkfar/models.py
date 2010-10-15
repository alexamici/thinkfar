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
    start_date = DateProperty(required=True)
    name = StringProperty(required=True, default=u'Default Portfolio')
    description = TextProperty()
    opening_transaction = ReferenceProperty(collection_name='opening_transaction_of') # one-way relation to Transaction
    default_cash_account = ReferenceProperty(collection_name='default_cash_account_of') # one-way relation to Account
    default_denomination = ReferenceProperty(collection_name='default_denomination_of') # one-way relation to Asset

    @property
    def id(self):
        return self.key().id()

    def __repr__(self):
        return u'<%s object name=%r owner=%r>' % \
            (self.__class__.__name__, self.name, self.owner.nickname())

    def _bootstrap(self):
        assert self.assets.count() == 0
        usd = Asset(portfolio=self, asset_model=AssetModel.get_by_name('Legal Currency'),
            name=u'USD Cash', identity=u'USD')
        usd.put()
        self.default_denomination = usd

        for definition in AccountDefinition.all():
            account = Account(definition=definition, denomination=usd, asset=None)
            account.put()

        usd_balance = Account(definition=self.account_by_code('1001').definition, denomination=usd, asset=usd)
        usd_balance.put()

        usd_bank = Asset(portfolio=self, asset_model=AssetModel.get_by_name('Bank Account'),
            name=u'USD Bank Account', identity=u'Default USD Bank Account')
        usd_bank.put()
        self.default_cash_account = usd_bank.default_value_account

        gold = Asset(portfolio=self, asset_model=AssetModel.get_by_name('Commodity Money'),
            name=u'Gold coins 1oz', identity=u'GOLD')
        gold.put()

        opening_transaction = Transaction(start_date=self.start_date, end_date=self.start_date, 
            description=u'Opening Balance')
        opening_transaction.put()
        self.opening_transaction = opening_transaction

        usd_bank.buy(1., price=0.)

    def put(self):
        if self.is_saved():
            return super(Portfolio, self).put()
        else:
            super(Portfolio, self).put()
            self._bootstrap()
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
        return Account.all().filter('denomination =', self.default_denomination).filter('asset =', asset).filter('definition !=', None)

    def leaf_accounts(self, code=None):
        all_leaf_accounts = Account.all().filter('denomination =', self.default_denomination).filter('asset !=', None)
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

    def accounts_by_codes(self, codes, asset=None):
        definitions = AccountDefinition.all().filter('code IN', codes)
        accounts = Account.all().filter('denomination =', self.default_denomination).filter('asset =', asset).filter('definition IN', list(definitions))
        if accounts.count() != len(codes):
            raise ValueError('%r %r' % (codes, list(accounts)))
        return accounts

    def simple_trade(self, asset, value, amount=1., taxes=0., fees=0., **keys):
        '''trade an asset using default accounts
        
        if date is None the trade is added to the opening balance for the accounts'''
        transaction = self.simple_transaction(asset.default_value_account, value, **keys)
        transaction.add_entries(((asset.inventory, amount),))
        transaction.put()

    def simple_transaction(self, credit_account, value, debit_account=None,
        start_date=None, end_date=None, asset=None, description=None):
        '''two-account transaction using default accounts
        
        if start_date is None the transaction is added to the opening balance for the accounts'''
        if start_date is None:
            assert end_date is None
            transaction = self.opening_transaction
            debit_account = self.account_by_code('3500') # equity
        else:
            if end_date is None:
                end_date = start_date
            transaction = Transaction(start_date=start_date, end_date=end_date, description=description)
            transaction.put()
            debit_account = debit_account or self.default_cash_account
        transaction.add_entries(((credit_account, value), (debit_account, - value)))
        transaction.put()
        return transaction

    def total_value(self, date):
        return sum(a.total_value(date) for a in self.assets)

    def estimated_yearly_revenue(self, year):
        return sum(a.estimated_yearly_revenue(year) for a in self.assets)

    def make_or_sync_yearend(self, year):
        yearends = Transaction.all().filter('descrioption =', 'yearend').filter('start_date=', date(year, 12, 31)).fetch(1)
        if len(yearends) == 0:
            yearend = Transaction(descrioption='yearend', start_date=date(year, 12, 31),
                end_date=date(year, 12, 31))
            yearend.put()
        else:
            yearend = yearends[0]
        for account in self.leaf_accounts():
            if not account.is_asset_account or account.definition.in_balance_sheet:
                continue
            balance = account.balance(date(year, 12, 31))
            if balance == 0:
                continue
            yearend.add_entries(((account, - balance), (self.account_by_code('3500'), balance)))

class AssetModel(Model):
    name = StringProperty(required=True)
    description = TextProperty()
    default_value_account_code = StringProperty()
    default_revenue_account_code = StringProperty()

    base_instances_keys = (
        {'name': 'Legal Currency', 'default_value_account_code': '1001'},
        {'name': 'Bank Account', 'default_value_account_code': '1002', 
            'description': 'Denominated in the main legal currency'},
        {'name': 'Commodity Money', 'default_value_account_code': '1007'},
        {'name': 'Commodity', 'default_value_account_code': '1122'},
        {'name': 'Land', 'default_value_account_code': '1600'},
        {'name': 'Building', 'default_value_account_code': '1680', 'default_revenue_account_code': '8141'},
        {'name': 'Vehicle', 'default_value_account_code': '1740'},
        {'name': 'Credit Card', 'default_value_account_code': '2707'},
        {'name': 'Job', 'default_value_account_code': '2010', 'default_revenue_account_code': '8000'},
        {'name': 'Time', 'default_value_account_code': '2070'},
        {'name': 'Need', 'default_value_account_code': '3450', 'default_revenue_account_code': '9130'}, # ARGH!
        {'name': 'Mortgage', 'default_value_account_code': '3141'},
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
    def default_value_account(self):
        return self.portfolio.account_by_code(self.asset_model.default_value_account_code, asset=self)

    @property
    def default_revenue_account(self):
        return self.portfolio.account_by_code(self.asset_model.default_revenue_account_code, asset=self)

    @property
    def inventory(self):
        for a in self.denomination_accounts:
            if a.definition is None:
                return a

    @property
    def has_identity(self):
        return self.identity is not None

    def __repr__(self):
        if self.has_identity:
            identification = u'identity=%r' % self.identity
        else:
            identification = u''
        return u'<%s object name=%r %s portfolio=%r owner=%r>' % \
            (self.__class__.__name__, self.name, identification,
                self.portfolio.name, self.portfolio.owner.nickname())

    def _bootstrap(self):
        assert self.denomination_accounts.count() == 0
        inventory = Account(definition=None, denomination=self)
        inventory.put()
        # during portfolio bootstrap we have no account
        try:
            default_value_account = Account(
                definition=self.portfolio.account_by_code(self.asset_model.default_value_account_code).definition,
                denomination=self.portfolio.default_denomination,
                asset=self
            )
            default_value_account.put()
        except AssertionError:
            pass
        if self.asset_model.default_revenue_account_code:
            default_revenue_account = Account(
                definition=self.portfolio.account_by_code(self.asset_model.default_revenue_account_code).definition,
                denomination=self.portfolio.default_denomination,
                asset=self
            )
            default_revenue_account.put()

    def put(self):
        if self.is_saved():
            return super(Asset, self).put()
        else:
            super(Asset, self).put()
            self._bootstrap()
            return super(Asset, self).put()

    def buy(self, amount=1., price=None, date=None, **keys):
        if price == None:
            price = amount
        self.portfolio.simple_trade(self, price, amount=amount, start_date=date, **keys)

    def sell(self, date, amount=1., value=None, **keys):
        if value == None:
            value = amount
        self.portfolio.simple_trade(self, - value, start_date=date, amount=-amount, **keys)

    def add_ammortization(self, date, value=None, **keys):
        self.portfolio.simple_transaction(self.default_value_account, - value, start_date=date, **keys)

    def reconcile(self, date, descpription=None, code='8212'):
        default_value_account_balance = self.default_value_account.balance(date)
        if default_value_account_balance == 0 or self.inventory.balance(date) != 0.:
            return
        profit_loss = Transaction(start_date=date, descpription=descpription)
        profit_loss.put()
        profit_loss_account = self.portfolio.account_by_code(code)
        profit_loss.add_entries(((self.default_value_account, - default_value_account_balance), (profit_loss_account, default_value_account_balance)))

    def account_by_code(self, code):
        return self.portfolio.account_by_code(code, asset=self)

    def accounts_by_codes(self, codes):
        return self.portfolio.accounts_by_codes(codes, asset=self)

    def add_account(self, code):
        account = Account(definition=self.portfolio.account_by_code(code).definition,
            denomination=self.portfolio.default_denomination, asset=self)
        account.put()
        return account

    def add_revenue(self, revenue, code=None, start_date=None, end_date=None, description=None):
        code = code or self.asset_model.default_revenue_account_code
        try:
            account = list(self.accounts_by_codes([code]))[0]
        except:
            account = self.add_account(code)
        end_date = end_date or start_date
        revenue_template = Transaction(start_date=start_date, end_date=end_date, description=description)
        revenue_template.put()
        revenue_template.add_entries(((account, -revenue), (self.portfolio.default_cash_account, revenue)))

    def total_value(self, date):
        return sum(a.balance(date) for a in self.accounts if a.definition.in_balance_sheet)

    def estimated_yearly_revenue(self, year):
        return - sum(a.partial_balance(date(year, 1, 1), date(year, 12, 31)) for a in self.accounts if not a.definition.in_balance_sheet)

# GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf
class AccountDefinition(Model):
    code = StringProperty(required=True)
    name = StringProperty(required=True)
    is_asset = BooleanProperty(default=False)
    is_liability = BooleanProperty(default=False)
    is_revenue = BooleanProperty(default=False)
    is_expense = BooleanProperty(default=False)
    description = TextProperty()
    parent_account = SelfReferenceProperty(collection_name='children_accounts')

    base_instances_keys = (
        {'code': '2599', 'name': 'Total assets', 'is_asset': True, 'children': (
            {'code': '1599', 'name': 'Total current assets', 'children': (
                {'code': '1001', 'name': 'Cash'},
                {'code': '1002', 'name': 'Deposits in local banks and institutions - local currency'},
                {'code': '1007', 'name': 'Other cash like instruments - gold bullion and silver bullion'},
                {'code': '1122', 'name': 'Inventory parts and supplies'},
            )},
            {'code': '2008', 'name': 'Total tangible capital assets', 'children': (
                {'code': '1600', 'name': 'Land'},
                {'code': '1680', 'name': 'Buildings'},
                {'code': '1740', 'name': 'Machinery, equipment, furniture, and fixtures'},
            )},
            {'code': '2178', 'name': 'Total intangible capital assets', 'children': (
                {'code': '2010', 'name': 'Intangible assets'},
                {'code': '2070', 'name': 'Resource rights'},
            )},
            {'code': '2589', 'name': 'Total long-term assets'},
        )},
        {'code': '3640', 'name': 'Total liabilities and shareholder equity', 'is_liability': True, 'children': (
            {'code': '3499', 'name': 'Total liabilities', 'children': (
                {'code': '2600', 'name': 'Bank overdraft'},
                {'code': '2707', 'name': 'Credit card loans'},
                {'code': '3141', 'name': 'Mortgages'},
                {'code': '3450', 'name': 'Long-term liabilities'},
            )},
            {'code': '3620', 'name': 'Total equity', 'children': (
                {'code': '3500', 'name': 'Common shares'},
            )},
        )},
        {'code': '8299', 'name': 'Total revenue', 'is_revenue': True, 'children': (
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
        {'code': '9368', 'name': 'Total expenses', 'is_expense': True, 'children': (
            {'code': '9367', 'name': 'Total operating expenses', 'children': (
                {'code': '8710', 'name': 'Interest and bank charges'},
                {'code': '8764', 'name': 'Government fees'},
                {'code': '9180', 'name': 'Property taxes'},
                {'code': '9130', 'name': 'Supplies'},
            )},
        )},
    )

    @property
    def id(self):
        return self.key().id()

    @property
    def in_balance_sheet(self):
        return self.is_asset or self.is_liability

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
        children_accounts = list(self.denomination.portfolio.accounts_by_codes(codes))
        children_accounts += self.denomination.portfolio.leaf_accounts(self.definition.code)
        set('account-%d-children_accounts' % self.id, children_accounts, time=3600)
        return children_accounts

    @property
    def is_inventory(self):
        return self.definition is None and self.asset is None

    @property
    def is_asset_account(self):
        return self.asset is not None

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

    def transactions(self):
        return [te.transaction for te in self.transaction_entries]

    def balance(self, date):
        balance = sum(a.balance(date) for a in self.children_accounts)
        return 0. + balance + sum(te.balance(date) for te in self.transaction_entries)

    def sign_balance(self, date):
        if (self.definition.is_liability or self.definition.is_revenue):
            return - self.balance(date)
        else:
            return self.balance(date)

    def partial_balance(self, start_date, end_date):
        children_balance = sum(a.partial_balance(start_date, end_date) for a in self.children_accounts)
        balance = 0. + children_balance + sum(te.partial_balance(start_date, end_date) for te in self.transaction_entries)
        return balance

    def total_credit(self, date):
        return sum(te.amount for te in self.transaction_entries if te.transaction.date <= date and te.amount > 0.)
    
    def total_debit(self, date):
        return sum(te.amount for te in self.transaction_entries if te.transaction.date <= date and te.amount < 0.)

class Transaction(Model):
    """An event in the double-entry book

    the event may have an time extension and in that case it really correspondes to a
    linear change in the accounts"""

    start_date = DateProperty(required=True)
    end_date = DateProperty(required=True)
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

    def balance(self, date):
        return self.partial_balance(self.transaction.start_date, date)

    def partial_balance(self, start_date, end_date):
        transaction = self.transaction
        start_date = transaction.start_date > start_date and transaction.start_date or start_date
        end_date = transaction.end_date < end_date and transaction.end_date or end_date
        delta_days = (end_date - start_date).days
        if delta_days < 0:
            return 0.
        if (transaction.end_date - transaction.start_date).days == 0:
            return self.amount
        return self.amount / (transaction.end_date - transaction.start_date).days * delta_days
