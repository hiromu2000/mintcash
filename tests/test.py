import os
import unittest
import mintcash
import json

class TestMintCash(unittest.TestCase):
    def setUp(self):
        email = os.environ.get("MINT_EMAIL", "")
        password = os.environ.get("MINT_PASSWORD","")
        dbname = os.environ.get("GNUCASH_DBNAME","")
        mapping = os.environ.get("MINTCASH_MAPPING","")
        assert email, 'Please set "MINT_EMAIL".'
        assert password, 'Please set "MINT_PASSWORD".'
        assert dbname, 'Please set "GNUCASH_DBNAME".'
        assert mapping, 'Please set "MINTCASH_MAPPING".'

        with open(mapping) as f:
            types = json.load(f)

        self.mint = mintcash.MintCash(email, password, dbname, types)

    def test_mirror_mint(self):
        self.mint.create_book()
        self.mint.add_accounts()
        self.mint.add_categories()
        self.mint.add_transactions()

        self.mint.add_transactions()
