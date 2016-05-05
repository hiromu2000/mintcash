import os
import unittest
import mintcash

class TestMintCash(unittest.TestCase):
    def setUp(self):
        email = os.environ.get("MINT_EMAIL", "")
        password = os.environ.get("MINT_PASSWORD","")
        dbname = os.environ.get("GNUCASH_DBNAME","")
        assert email, 'Please set "MINT_EMAIL".'
        assert password, 'Please set "MINT_PASSWORD".'
        assert dbname, 'Please set "GNUCASH_DBNAME".'

        self.mint = mintcash.MintCash(email, password, dbname)

    def test_mirror_mint(self):
        self.mint.create_book()
        self.mint.add_accounts()
        self.mint.add_transactions()

        self.mint.add_transactions()
