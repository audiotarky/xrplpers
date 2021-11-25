import unittest
from xrplpers.nfts.entities import TransferFee


class testVerification(unittest.TestCase):
    def testLowerBound(self):
        with self.assertRaises(ValueError):
            TransferFee(-1)

    def testUpperBound(self):
        with self.assertRaises(ValueError):
            TransferFee(5001)

    def testLowerBoundFromPercent(self):
        with self.assertRaises(ValueError):
            TransferFee.from_percent(-1)

    def testUpperBoundFromPercent(self):
        with self.assertRaises(ValueError):
            TransferFee.from_percent(51)

    def testFromPercent(self):
        t = TransferFee.from_percent(50)
        self.assertEqual(t.value, t.max)
        self.assertEqual(t.as_percent(), 50)

    def testFromSpecPercent314(self):
        t = TransferFee.from_percent(3.14)
        t.value = 314

    def testFromSpecPercent314(self):
        t = TransferFee.from_percent(0.01)
        t.value = 1

    def testMustBeInt(self):
        with self.assertRaises(TypeError):
            TransferFee("foo")

    def testMustBeIntFromPercent(self):
        with self.assertRaises(TypeError):
            TransferFee.from_percent("foo")
