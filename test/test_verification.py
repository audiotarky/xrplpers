import json
from pathlib import Path
import unittest
from xrplpers.verification import TransactionVerifier, Signer
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec import decode


class testVerification(unittest.TestCase):
    def setUp(self):
        # These fixtures are taken from https://github.com/XRPL-Labs/verify-xrpl-signature/
        # Used under the MIT license
        # https://raw.githubusercontent.com/XRPL-Labs/verify-xrpl-signature/master/test/fixtures.json
        json_file = Path(__file__).parent / Path("fixture_verification.json")
        self.fixtures = json.loads(json_file.read_text())

    def testSingleSign(self):
        v = TransactionVerifier(self.fixtures["valid"]["blob"])
        self.assertTrue(v.is_valid())
        self.assertFalse(v.is_multisigned())
        self.assertEqual(self.fixtures["valid"]["account"], v.signed_by_account())

    def testMultiSignValid(self):
        v = TransactionVerifier(self.fixtures["multisign"]["blob"])
        self.assertTrue(v.is_valid())

    def testMultiSignValidWithSigner(self):
        s = Signer(
            self.fixtures["multisign"]["pubkey"],
            None,
            self.fixtures["multisign"]["account"],
        )
        v = TransactionVerifier(self.fixtures["multisign"]["blob"], s)
        self.assertTrue(v.is_valid())

    def testMultiSigned(self):
        v = TransactionVerifier(self.fixtures["multisign"]["blob"])
        self.assertTrue(v.is_multisigned())

    def testMultiSignSigner(self):
        v = TransactionVerifier(self.fixtures["multisign"]["blob"])
        self.assertEqual(self.fixtures["multisign"]["account"], v.signed_by_account())

    def testInvalid(self):
        with self.assertRaises(XRPLBinaryCodecException):
            v = TransactionVerifier(self.fixtures["invalid"]["blob"])


if __name__ == "__main__":
    unittest.main()
