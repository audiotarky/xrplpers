from xrplpers.nfts.entities import TokenID, TokenFlags
import unittest

from xrpl.core.binarycodec.types.account_id import AccountID


class testTokenFromHex(unittest.TestCase):
    def setUp(self):
        self.token_hex = (
            "000B013A95F14B0E44F78A264E41713C64B5F89242540EE2BC8B858E00000D65"
        )

    def testSequence(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.sequence, 3429)

    @unittest.skip
    def testTaxon(self):
        """
        Skipping until the unscrambling of taxons is understood
        """
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.taxon, 146999694)

    def testIssuer(self):
        t = TokenID.from_hex(self.token_hex)
        a = AccountID.from_value("rNCFjv8Ek5oDrNiMJ3pw6eLLFtMjZLJnf2")
        self.assertEqual(t.issuer.to_json(), a.to_json())

    def testTransferFee(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.transfer_fee.as_percent(), 0.314)

    def testFlags(self):
        t = TokenID.from_hex(self.token_hex)
        for flag in [
            TokenFlags.lsfBurnable,
            TokenFlags.lsfOnlyXRP,
            TokenFlags.lsfTransferable,
        ]:
            self.assertIn(flag, t.flags)

    def testIssuerAsString(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.issuer_as_string, "rNCFjv8Ek5oDrNiMJ3pw6eLLFtMjZLJnf2")

    def testToStringFlags(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.to_str()[:4], self.token_hex[:4])
        self.assertEqual(t.to_str()[:4], "000B")

    def testToStringFee(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.to_str()[4:8], self.token_hex[4:8])
        self.assertEqual(t.to_str()[4:8], "013A")

    def testToStringIssuer(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.to_str()[8:48], self.token_hex[8:48])
        self.assertEqual(t.to_str()[8:48], "95F14B0E44F78A264E41713C64B5F89242540EE2")

    def testToStringTaxon(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.to_str()[48:56], self.token_hex[48:56])
        self.assertEqual(t.to_str()[48:56], "BC8B858E")

    def testToStringSequence(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.to_str()[56:64], self.token_hex[56:64])
        self.assertEqual(t.to_str()[56:64], "00000D65")

    @unittest.skip
    def testToStringRoundtrip(self):
        t = TokenID.from_hex(self.token_hex)
        self.assertEqual(t.to_str(), self.token_hex)
