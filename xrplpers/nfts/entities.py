"""
https://github.com/XRPLF/XRPL-Standards/discussions/46 proposes two new
objects and one new ledger structure:

- An NFToken is a new object that describes a single NFT.
- An NFTokenOffer is a new object that describes an offer to buy or sell a
  single NFToken.
- An NFTokenPage is a ledger structure that contains a set of NFToken objects
  owned by the same account.
"""


from dataclasses import dataclass
from enum import IntFlag
from struct import Struct

from xrpl.core.binarycodec.types.account_id import AccountID


class TokenFlags(IntFlag):
    # If set, indicates that the issuer (or an entity authorized by the
    # issuer) can destroy the object. The object's owner can always do so.
    lsfBurnable = int(0x0001)
    # If set, indicates that the tokens can only be offered or sold for XRP.
    lsfOnlyXRP = int(0x0002)
    # If set, indicates that the issuer wants a trustline to be automatically
    # created.
    lsfTrustLine = int(0x0004)
    # If set, indicates that this NFT can be transferred. This flag has no
    # effect if the token is being transferred from the issuer or to the
    # issuer.
    lsfTransferable = int(0x0008)
    # This proposal reserves this flag for future use. Attempts to set this
    # flag should fail.
    lsfReservedFlag = int(0x8000)


@dataclass
class TransferFee:
    value: int
    min: int = 0
    max: int = 5000

    def __post_init__(self):
        if not (self.min <= self.value <= self.max):
            raise ValueError(f"TransferFee must be between {self.min} & {self.max}")

    def as_percent(self):
        return self.value / 100

    @classmethod
    def from_percent(cls, value):
        return cls(value * 100)


class Taxon:
    """
    f(x)=(m*x+c) mod n
    """

    m = 384160001
    c = 2459
    n = 200

    @classmethod
    def scramble(cls, sequence):
        return (cls.m * sequence + cls.c) % n


class TokenID:
    struct = Struct("2s2s20s4s4s")

    def __init__(self, flags, transfer_fee, issuer, taxon=None, sequence=None):
        self.flags = flags
        self.transfer_fee = transfer_fee
        self.issuer = issuer
        self.taxon = taxon
        self.sequence = sequence

    @classmethod
    def from_hex(cls, token_hex):
        """
        Load the token from a hex string

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
        token_bytes = bytes.fromhex(token_hex)
        flags, transfer_fee, issuer, taxon, sequence = cls.struct.unpack(token_bytes)
        return cls(
            TokenFlags(int.from_bytes(flags, byteorder="big")),
            TransferFee(int.from_bytes(transfer_fee, byteorder="big")),
            AccountID.from_value(issuer.hex().upper()),
            int.from_bytes(taxon, byteorder="big"),
            int.from_bytes(sequence, byteorder="big"),
        )

    def __str__(self) -> str:
        return f"NFTToken issued by {self.issuer} with a transfer fee of {self.transfer_fee}"


class NFTToken:
    id: TokenID
    uri: str

    def burn(self):
        """
        NFTs can be destroyed by the NFTokenBurn transaction
        """
        pass

    @classmethod
    def mint(self, data):
        """
        NFTs are created using the NFTokenMint transaction
        """
        pass


class NFTokenOffer:
    pass


class NFTokenPage:
    pass
