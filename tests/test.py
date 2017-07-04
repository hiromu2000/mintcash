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
        ius_session = os.environ.get("IUS_SESSION","")
        thx_guid = os.environ.get("THX_GUID","")
        assert email, 'Please set "MINT_EMAIL".'
        assert password, 'Please set "MINT_PASSWORD".'
        assert dbname, 'Please set "GNUCASH_DBNAME".'
        assert mapping, 'Please set "MINTCASH_MAPPING".'
        assert ius_session, 'Please set "IUS_SESSION".'
        assert thx_guid, 'Please set "THX_GUID".'

        with open(mapping) as f:
            types = json.load(f)

        self.mint = mintcash.MintCash(email, password, ius_session, thx_guid, dbname, types)

    def test_mirror_mint(self):
        self.mint.create_book()
        self.mint.add_accounts()
        self.mint.add_categories()
        self.mint.add_transactions()

        self.mint.add_transactions()
