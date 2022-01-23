from xrplpers.nfts.entities import NFToken
import unittest
from pathlib import Path
import json
from xrpl.core.binarycodec.types.account_id import AccountID


class testNFToken(unittest.TestCase):
    def testFromTransaction(self):
        with Path("test/fixture_submitted_mint_transaction.json").open() as f:
            fixture = json.load(f)
            token = NFToken.from_transaction(fixture)
            self.assertEqual(token.id.flags, fixture["Flags"])
            self.assertEqual(token.id.issuer.to_json(), fixture["Issuer"])
            # self.assertEqual(token.id.issuer, fixture["Issuer"])
            # self.assertEqual(token.id.issuer, fixture["Issuer"])
