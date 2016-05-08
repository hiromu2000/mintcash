import mintapi
import piecash
from decimal import Decimal, getcontext

class MintCash(object):
    mint = None
    dbname = None
    types = {
        'ASSET': {'name': 'Assets', 'gnucash_type': 'ASSET'},
        'LIABILITY': {'name': 'Liabilities', 'gnucash_type': 'LIABILITY'},
        'EXPENSE': {'name': 'Expenses', 'gnucash_type': 'EXPENSE'},
        'INCOME': {'name': 'Income', 'gnucash_type': 'INCOME'},
        'EQUITY': {'name': 'Equity', 'gnucash_type': 'EQUITY'},
        'NO_CATEGORY': {'name': 'No_category', 'gnucash_type': 'ASSET'}
    }

    def __init__(self, email=None, password=None, dbname=None):
        self.mint = mintapi.Mint(email, password)
        self.dbname = dbname

    def create_book(self):
        book = piecash.create_book(sqlite_file=self.dbname, currency='USD')
        book.save()
        book.close()

    def add_accounts(self):
        book = piecash.open_book(sqlite_file=self.dbname, readonly=False)
        USD = book.commodities.get(mnemonic='USD')
        types = self.types

        # Create level=1 Gnucash accounts
        for type, values in types.iteritems():
            piecash.Account(name=values['name'],
                            type=values['gnucash_type'],
                            parent=book.root_account,
                            commodity=USD,
                            placeholder=True)

        # Create level=2 Gnucash accounts for Mint accounts
        for account in self.mint.get_accounts():
            if account['accountType'].upper() == 'CREDIT':
                parent = book.accounts(name=types['LIABILITY']['name'])
            else:
                parent = book.accounts(name=types['ASSET']['name'])
            piecash.Account(name=account['accountName'],
                            type=account['accountType'].upper(),
                            parent=parent,
                            commodity=USD)
        book.save()
        book.close()

    def add_categories(self):
        book = piecash.open_book(sqlite_file=self.dbname, readonly=False)
        USD = book.commodities.get(mnemonic='USD')
        types = self.types

        # Create level=2 Gnucash accounts for Mint depth=1 categories
        categories = {}
        for category in self.mint.get_categories().itervalues():
            categories[category['id']] = category
            parent = category['parent']
            categories[parent['id']] = parent

        for category in categories.itervalues():
            if category['depth'] == 1:
                acc = piecash.Account(name=category['name'],
                                type=types[category['categoryType']]['gnucash_type'],
                                parent=book.accounts(name=types[category['categoryType']]['name']),
                                code=str(category['id']),
                                commodity=USD)

        # Create level=3 Gnucash accounts for Mint depth=2 categories
        for category in categories.itervalues():
            if category['depth'] == 2:
                piecash.Account(name=category['name'],
                                type=types[category['categoryType']]['gnucash_type'],
                                parent=book.accounts(code=str(category['parent']['id'])),
                                code=str(category['id']),
                                commodity=USD)
        book.save()
        book.close()

    def add_transactions(self):
        book = piecash.open_book(sqlite_file=self.dbname, readonly=False)
        USD = book.commodities.get(mnemonic='USD')

        for index, tran in self.mint.get_detailed_transactions().iterrows():
            if [tr for tr in book.transactions if tr.num==str(tran['id'])]:
                #print 'already exists', tran['odate'], tran['merchant'], tran['amount']
                continue

            a1 = book.accounts(code=str(tran['categoryId']))
            a2 = book.accounts(name=tran['account'])
            amount = Decimal("%.2f" % tran['amount'])

            piecash.Transaction(currency=USD,
                                description=tran['merchant'],
                                splits=[
                                    piecash.Split(account=a1, value=amount),
                                    piecash.Split(account=a2, value=-1 * amount)
                                ],
                                post_date=tran['odate'].to_datetime(),
                                num=str(tran['id']))
        book.save()
        book.close()
