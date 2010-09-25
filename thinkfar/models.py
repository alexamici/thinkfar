# 'Price is what you pay. Value is what you get.' Warren Buffett, 2008.

from datetime import date

from google.appengine.ext.db import Model, FloatProperty, StringProperty, BooleanProperty
from google.appengine.ext.db import TextProperty, DateProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty


class Root(object):
    title = u'think beyond the end of your nose'

root = Root()

def get_root(request):
    return root


class Portfolio(Model):
    owner = UserProperty(required=True)
    name = StringProperty(required=True, default=u'Default Portfolio')
    description = TextProperty()

    @property
    def id(self):
        return self.key().id()

    def put(self):
        if self.is_saved():
            return super(Portfolio, self).put()
        key = super(Portfolio, self).put()
        currency = AssetModel.all().filter('name =', 'Currency').fetch(1)[0]
        usd = Asset(portfolio=self, asset_model=currency, name='Cash USD', identity='USD')
        usd.put()
        eur = Asset(portfolio=self, asset_model=currency, name='Cash EUR', identity='EUR')
        eur.put()
        gold = Asset(portfolio=self, asset_model=currency, name='Cash GOLD', identity='GOLD')
        gold.put()
        for definition in AccountDefinition.all():
            account = Account(definition=definition, denomination=usd)
            account.put()
        return key

    @property
    def default_cash_asset(self):
        return Asset.all().filter('name =', 'Cash USD').filter('portfolio =', self).fetch(1)[0]

    def default_cash_opening_balance(self, amount):
        opening_balance = Transaction(date=date(2000, 1, 1), description='Opening Balance')
        opening_balance.put()
        opening_balance.add_entries((
            (self.default_cash_asset.parent_account, amount),
            # equity
            (self.account_by_code('3620'), - amount),
        ))

    def total_accounts(self):
        return [a for a in Account.all().filter('denomination =', self.default_cash_asset)
            if a.definition and a.definition.parent_account is None]

    def total_balance_sheet_accounts(self):
        return [a for a in self.total_accounts() if a.definition.in_balance_sheet]

    def accounts(self):
        return Account.all().filter('denomination =', self.default_cash_asset)

    def all_accounts(self):
        return Account.all().filter('denomination IN', list(self.assets))

    def account_by_code(self, code):
        accounts = [a for a in self.accounts() if a.definition and a.definition.code == code]
        if len(accounts) == 0:
            raise ValueError('No account with code %r' % code)
        elif len(accounts) > 1:
            raise ValueError('Multiple accounts with code %r' % code)
        return accounts[0]

    def __repr__(self):
        return u'<%s object name=%r owner=%r>' % \
            (self.__class__.__name__, self.name, self.owner.nickname())

class AssetModel(Model):
    name = StringProperty(required=True)
    description = TextProperty()
    parent_account_code = StringProperty()

    base_instances = (
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
        return self.portfolio.account_by_code(self.asset_model.parent_account_code)

    @property
    def has_identity(self):
        return self.identity is not None

    def put(self):
        if self.is_saved():
            return super(Asset, self).put()
        key = super(Asset, self).put()
        balance = Account(definition=None, denomination=self)
        balance.put()
        return key

    def buy(self, amount=1., price=None, **keys):
        if price == None:
            price = amount
        self.trade(amount=amount, value=-price, **keys)

    def sell(self, amount=1., value=None, **keys):
        if value == None:
            value = amount
        self.trade(amount=-amount, value=value, **keys)

    def trade(self, value=None, taxes=0., fees=0.,
            date=None, amount=None, description=None, account=None):
        if account is None:
            account = self.portfolio.default_cash_asset.parent_account
        trade = Transaction(date=date, description=description)
        trade.put()
        trade.add_entries(((self.account, amount), (account, value), (self.parent_account, -value)))

    @property
    def account(self):
        for a in self.accounts:
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

    base_instances = (
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
        {'code': '3499', 'name': 'Total liabilities', 'children': (
            {'code': '3139', 'name': 'Total current liabilities', 'children': (
                {'code': '2600', 'name': 'Bank overdraft'},
                {'code': '2707', 'name': 'Credit card loans'},
            )},
            {'code': '3450', 'name': 'Total long-term liabilities', 'children': (
                {'code': '3141', 'name': 'Mortgages'},
            )},
        )},
        {'code': '3620', 'name': 'Total equity'},
        {'code': '8299', 'name': 'Total revenue', 'in_balance_sheet': False},
        {'code': '9368', 'name': 'Total expenses', 'in_balance_sheet': False},
    )

    @property
    def id(self):
        return self.key().id()

class Account(Model):
    # if definition is None the account is the balance of the denomination asset
    definition = ReferenceProperty(AccountDefinition, collection_name='accounts')
    denomination = ReferenceProperty(Asset, required=True, collection_name='accounts')

    @property
    def children_accounts(self):
        if self.definition is None:
            return []
        codes = [am.code for am in self.definition.children_accounts]
        return [self.denomination.portfolio.account_by_code(c) for c in codes]

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
        return u'<%s object denomination=%r name=%r code=%r in_balance_sheet=%r>' % \
            (self.__class__.__name__, self.denomination.identity, name, code, in_balance_sheet)

class Transaction(Model):
    date = DateProperty(required=True)
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

    @property
    def id(self):
        return self.key().id()
