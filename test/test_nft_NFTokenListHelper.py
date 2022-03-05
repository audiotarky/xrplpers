from xrplpers.nfts.entities import NFTokenListHelper
import unittest
from pathlib import Path
import json


class testNFToken(unittest.TestCase):
    def testFromTransaction(self):
        with Path("test/fixture_submitted_mint_transaction.json").open() as f:
            fixture = json.load(f)
            list = NFTokenListHelper()
            new, added = list.add_from_transaction(fixture)
            self.assertEqual(len(list), 29)
            self.assertEqual(len(added), len(list))
            self.assertEqual(len(new), 1)

    def testInitFromTransaction(self):
        with Path("test/fixture_submitted_mint_transaction.json").open() as f:
            fixture = json.load(f)
            list = NFTokenListHelper(transaction=fixture)
            self.assertEqual(len(list), 29)
