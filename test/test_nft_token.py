from xrplpers.nfts.entities import NFToken, TokenFlags
import unittest


class testTokenFromHex(unittest.TestCase):
    def setUp(self):
        """
        From the spec:

        This composite field uniquely identifiers a token; it contains:

        a byte is equal to 8 bits

        - a set of 16 bits that identify flags or settings specific to the NFT
        - 16 bits that encode the transfer fee associated with this token, if
          any
        - 160-bit account identifier of the issuer
        - a 32-bit issuer-specified taxon
        - an (automatically generated) monotonically increasing 32-bit
          sequence number.

        The 16-bit flags and transfer fee fields, and the 32-bit taxon and
        sequence number fields are stored in big-endian format.
        """
        self.token_hex = (
            "000B013A95F14B0E44F78A264E41713C64B5F89242540EE2BC8B858E00000D65"
        )

    def testSequence(self):
        t = NFToken.from_hex(self.token_hex)
        self.assertEqual(t.sequence, 3429)

    def testTaxon(self):
        t = NFToken.from_hex(self.token_hex)
        self.assertEqual(t.taxon, 146999694)

    def testIssuer(self):
        t = NFToken.from_hex(self.token_hex)
        self.assertEqual(t.issuer, "rNCFjv8Ek5oDrNiMJ3pw6eLLFtMjZLJnf2")

    def testTransferFee(self):
        t = NFToken.from_hex(self.token_hex)
        self.assertEqual(t.transfer_fee.as_percent(), 3.14)

    def testFlags(self):
        t = NFToken.from_hex(self.token_hex)
        for flag in [
            TokenFlags.lsfBurnable,
            TokenFlags.lsfOnlyXRP,
            TokenFlags.lsfTransferable,
        ]:
            self.assertIn(flag, t.flags)
