import mintapi
import piecash
from decimal import Decimal, getcontext

class MintCash(object):
    mint = None
    dbname = None
    types = None

    def __init__(self, email=None, password=None, ius_session=None, thx_guid=None, dbname=None, types=None):
        self.mint = mintapi.Mint(email, password, headless=True, mfa_method = "sms")
        self.dbname = dbname
        self.types = types

    def create_book(self):
        book = piecash.create_book(uri_conn=self.dbname, currency='USD')
        book.save()
        book.close()

    def add_accounts(self):
        book = piecash.open_book(uri_conn=self.dbname, readonly=False, do_backup=False)
        USD = book.commodities.get(mnemonic='USD')
        types = self.types

        # Create level=1 Gnucash accounts
        for type, values in types.iteritems():
            acc = piecash.Account(name=values['name'],
                            type=values['gnucash_type'],
                            parent=book.root_account,
                            commodity=USD,
                            placeholder=True)
            try:
                book.save()
            except ValueError:
                #print '%s already exists!' % acc.name
                book.cancel()

        # Create level=2 Gnucash accounts for Mint accounts
        for account in self.mint.get_accounts():
            if account['accountType'].upper() == 'CREDIT':
                parent = book.accounts(name=types['LIABILITY']['name'])
            else:
                parent = book.accounts(name=types['ASSET']['name'])
            acc = piecash.Account(name=account['accountName'],
                            type=account['accountType'].upper(),
                            parent=parent,
                            commodity=USD)
            try:
                book.save()
            except ValueError:
                #print '%s already exists!' % acc.name
                book.cancel()
        book.close()

    def add_categories(self):
        book = piecash.open_book(uri_conn=self.dbname, readonly=False, do_backup=False)
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
                try:
                    book.save()
                except ValueError:
                    #print '%s already exists!' % acc.name
                    book.cancel()

        # Create level=3 Gnucash accounts for Mint depth=2 categories
        for category in categories.itervalues():
            if category['depth'] == 2:
                acc = piecash.Account(name=category['name'],
                                type=types[category['categoryType']]['gnucash_type'],
                                parent=book.accounts(code=str(category['parent']['id'])),
                                code=str(category['id']),
                                commodity=USD)
                try:
                    book.save()
                except ValueError:
                    #print '%s already exists!' % acc.name
                    book.cancel()
        book.close()

    def add_transactions(self):
        book = piecash.open_book(uri_conn=self.dbname, readonly=False, do_backup=False)
        USD = book.commodities.get(mnemonic='USD')

        cnt = 0
        for index, tran in self.mint.get_detailed_transactions().iterrows():
            if cnt > 10:
                break
            if [tr for tr in book.transactions if tr.num==str(tran['id'])]:
                #print 'already exists', tran['odate'], tran['merchant'], tran['amount']
                cnt = cnt + 1
                continue
            if tran['isDuplicate']:
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
                                post_date=tran['odate'].to_pydatetime().date(),
                                num=str(tran['id']))
        book.save()
        book.close()
