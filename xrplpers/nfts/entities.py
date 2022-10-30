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
from struct import Struct, pack
import typing
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.models.transactions import (
    Memo,
    NFTokenMint,
)
from xrpl.transaction import (
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
    safe_sign_and_submit_transaction,
)
from xrpl.utils import str_to_hex, hex_to_str
import json


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
    max: int = 50000

    def __post_init__(self):
        if not (self.min <= self.value <= self.max):
            raise ValueError(f"TransferFee must be between {self.min} & {self.max}")

    def as_percent(self):
        return self.value / 1000

    @classmethod
    def from_percent(cls, value):
        return cls(value * 1000)

    def to_bytes(self):
        return self.value.to_bytes(2, byteorder="big")


class Taxon:
    """
    f(x)=(m*x+c) mod n
    """

    m = 384160001
    c = 2459
    n = 200
    value = 0

    def __init__(self, value: int) -> None:
        self.value = value

    @classmethod
    def scramble(cls, sequence):
        return (cls.m * sequence + cls.c) % n

    @classmethod
    def from_bytes(cls, taxon_bytes):
        return cls(int.from_bytes(taxon_bytes, byteorder="big"))

    @property
    def as_bytes(self):
        return self.value.to_bytes(4, byteorder="big")


class TokenID:
    struct = Struct("2s2s20s4s4s")

    def __init__(
        self,
        flags: TokenFlags,
        transfer_fee: TransferFee,
        issuer: AccountID,
        taxon: Taxon,
        sequence: int,
    ):
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
            Taxon.from_bytes(taxon),
            int.from_bytes(sequence, byteorder="big"),
        )

    @classmethod
    def from_mint_txn(cls, mint):
        """
        NFTokenMint(
            account='rawtybaJBgwuUcaNv28Q4YnvqQj1mowz41',
            transaction_type=<TransactionType.NFTOKEN_MINT: 'NFTokenMint'>,
            fee='10',
            sequence=177354,
            account_txn_id=None,
            flags=8,
            last_ledger_sequence=191768,
            memos=[Memo(memo_data='4d696e74656420627920417564696f7461726b7920617420323032322d30312d32312031303a32383a35342e343332343034',
            memo_format=None,
            memo_type=None)],
            signers=None,
            source_tag=None,
            signing_pub_key='03FE3207F849C5C0BC16E3479BBD0A8B8B2F0482A5AA62A5ECCAD062AEC43FDD9C',
            txn_signature='304502210082A726527F9269C5E8979B52F8259D37E0D3B9A274A9765B1D8CE00855B3CFF302203494DAF8FCBDAD91A090F3615110F80EF67A0EB85A3E2427E192ED98C8EBEBF1',
            token_taxon=0,
            issuer='rJhSM8539zfoQwq7NomvEvt9xSbppf38Ng',
            transfer_fee=25000,
            uri='68747470733a2f2f6e66742e617564696f7461726b792e636f6d2f615f6c6f6e675f68617368'
        )

        """
        return cls(
            TokenFlags(mint.flags),
            TransferFee(int(mint.fee)),
            AccountID.from_value(mint.account),
            Taxon(mint.token_taxon),
            mint.sequence,
        )

    def to_str(self) -> str:
        """
        Pack the object into the hex string.
        """
        s = self.struct.pack(
            self.flags.to_bytes(2, byteorder="big"),
            self.transfer_fee.to_bytes(),
            self.issuer.__bytes__(),
            self.taxon.as_bytes,
            self.sequence.to_bytes(4, byteorder="big"),
        )
        return s.hex().upper()

    def __str__(self) -> str:
        return f"NFToken issued by {self.issuer} with a transfer fee of {self.transfer_fee}"

    @property
    def issuer_as_string(self):
        return self.issuer.to_json()

    @property
    def as_dict(self):
        return {
            flags: self.flags,
            transfer_fee:  self.transfer_fee,
            issuer: self.issuer,
            taxon: self.taxon,
            sequence: self.sequence
        }

def _flatten_nft_node(node):
    return [x["NonFungibleToken"]["TokenID"] for x in node]


class BadTransactionError(Exception):
    def __init__(self, transaction=None, *args, **kwargs):
        # Call the base class constructor with the parameters it needs
        super().__init__(args, kwargs)
        self.transaction = transaction


class NFToken:
    def __init__(self, id: TokenID, uri: str, txn=None) -> None:
        self.id = id
        self.uri = uri
        self.transaction_id = txn

    def burn(self):
        """
        NFTs can be destroyed by the NFTokenBurn transaction
        """
        pass

    @classmethod
    def mint(cls, minter, url, client, creator=None, message="", fee=0):
        """
        NFTs are created using the NFTokenMint transaction
        """

        kwargs = {
            "account": minter.classic_address,
            "flags": 8,
            "uri": str_to_hex(url),
            "transfer_fee": fee,
            "token_taxon": 0,
        }
        if creator and minter.classic_address != creator.classic_address:
            kwargs["issuer"] = creator.classic_address

        if message:
            memo = Memo.from_dict({"memo_data": str_to_hex(message)})
            memo.validate()
            kwargs["memos"] = [memo]

        nft = NFTokenMint(**kwargs)
        nft.validate()
        tx_signed = safe_sign_and_autofill_transaction(nft, minter, client)
        nft_tx = send_reliable_submission(tx_signed, client)

        token = NFToken.from_transaction(nft_tx.result)
        return token

    @classmethod
    def from_transaction(cls, txn):
        """
        Create a representation of an NFToken from an NFTokenMint transaction
        """
        if txn["TransactionType"] != "NFTokenMint":
            raise BadTransactionError("Transaction is not an NFTokenMint", txn)
        if txn["meta"]["TransactionResult"] != "tesSUCCESS":
            raise BadTransactionError("Transaction was not successful", txn)
        nft_id = ""
        before = set()
        after = set()
        for n in txn["meta"]["AffectedNodes"]:
            v = list(n.values())[0]
            if v["LedgerEntryType"] == "NFTokenPage":
                try:
                    if "PreviousFields" in v:
                        before = (
                            set(
                                _flatten_nft_node(
                                    v["PreviousFields"]["NonFungibleTokens"]
                                )
                            )
                            | before
                        )
                    if "FinalFields" in v:
                        after = (
                            set(
                                _flatten_nft_node(v["FinalFields"]["NonFungibleTokens"])
                            )
                            | after
                        )
                except:
                    raise BadTransactionError(
                        "Could not parse expected transaction fields", transaction=txn
                    )
        nft_id = (after - before).pop()
        return cls(
            TokenID.from_hex(nft_id),
            hex_to_str(txn["URI"]),
            txn["hash"],
        )


class NFTokenListHelper:
    """
    Helper class that can hold a list of NFTs in various states;
    - to be minted
    - owned by an account
    - found in a transaction node
    - printable/serialised to human formats
    """

    def __init__(self, list=[], transaction={}) -> None:
        self._nfts = set()
        self.add_from_list(list)
        if transaction:
            self.add_from_transaction(transaction)

    def __add__(self, nft):
        # https://www.tutorialsteacher.com/python/magic-methods-in-python
        self._nfts.add(tuple(nft.items()))

    def __sub__(self, nft):
        self._nfts.discard(tuple(nft.items()))

    def add(self, nft):
        self + nft

    def __len__(self):
        return len(self._nfts)

    def __str__(self):
        return json.dumps([dict(i) for i in self._nfts])

    def add_from_list(self, list):
        """
        Create NFToken objects for a series of {TokenID, URI} dicts and to the NFTokenListHelper.
        """
        self._nfts |= set(list)

    def add_from_transaction(self, txn):
        """
        Given a transaction, find any NFT added to the wallet, add it to the
        NFTokenListHelper and return the NFTs that have been added in the
        transaction, and that are new to the listto the list.
        """
        before = set()
        after = set()

        for n in txn["meta"]["AffectedNodes"]:
            # Cast the dict values view to a list so we can easily get the single entry
            v = list(n.values())[0]
            if v["LedgerEntryType"] == "NFTokenPage":
                try:
                    if "PreviousFields" in v:
                        before = (
                            set(
                                _flatten_nft_node(
                                    v["PreviousFields"]["NonFungibleTokens"]
                                )
                            )
                            | before
                        )
                    if "FinalFields" in v:
                        after = (
                            set(
                                _flatten_nft_node(v["FinalFields"]["NonFungibleTokens"])
                            )
                            | after
                        )
                except:
                    raise BadTransactionError(
                        "Could not parse expected transaction fields", transaction=txn
                    )

        new_nft_in_txn = NFTokenListHelper(after - before)
        new_to_list = NFTokenListHelper((before | after) - self._nfts)

        self.add_from_list(before | after)
        return new_nft_in_txn, new_to_list


class NFTokenOffer:
    pass


class NFTokenPage:
    type = 0x0050
    next_page: str = ""
    prev_page: str = ""
    nfts: typing.List[dict] = []

    def add(self, nft):
        if len(self.nfts) >= 32:
            raise

    pass
