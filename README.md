# mintcash
Transfer transactions from Mint.com to Gnucash

# How to test

```
$ pwd
/home/ubuntu/mintcash
$ export MINT_EMAIL='foo@example.com'
$ export MINT_PASSWORD='yourpassword'
$ export GNUCASH_DBNAME='sqlite:///test.gnucash'
$ export MINTCASH_MAPPING='mappings/default.json'
$ export IUS_SESSION='your_ius_session'
$ export THX_GUID='your_thx_guid'
$ nosetests
```
