from xrpl.core.binarycodec import decode, encode_for_signing, encode_for_multisigning  # type: ignore
from xrpl.core.keypairs import is_valid_message, derive_classic_address  # type: ignore
import json
from collections import namedtuple

Signer = namedtuple("Signer", "SigningPubKey,TxnSignature,Account")


def signer_generator(signers: list):
    for s in signers:
        yield Signer(**s["Signer"])


class TransactionVerifier:
    def __init__(self, transaction_hex: str, signer: Signer = None) -> None:
        self.transaction_hex = transaction_hex
        self.decoded_transaction = decode(transaction_hex)
        self.signers = []
        self.multi_sign = False

        if "Signers" in self.decoded_transaction:
            self.multi_sign = True
            if signer:
                for s in signer_generator(self.decoded_transaction["Signers"]):
                    if (
                        s.SigningPubKey == signer.SigningPubKey
                        and s.Account == signer.Account
                    ):
                        self.signers.append(s)
                        break
            for s in signer_generator(self.decoded_transaction["Signers"]):
                self.signers.append(s)
        else:
            self.signers.append(
                Signer(
                    **{
                        k: v
                        for k, v in self.decoded_transaction.items()
                        if k in Signer._fields
                    }
                )
            )

    def is_valid(self) -> bool:
        return is_valid_message(
            bytes.fromhex(self.encoded_transaction()),
            bytes.fromhex(self.signer().TxnSignature),
            self.signer().SigningPubKey,
        )

    def signer(self) -> Signer:
        return self.signers[0]

    def signed_by_account(self) -> str:
        signer = self.signer()
        if signer.Account.startswith("r"):
            return signer.Account
        else:
            return derive_classic_address(signer.SigningPubKey)

    def is_multisigned(self) -> bool:
        return self.multi_sign

    def encoded_transaction(self) -> str:
        if self.multi_sign:
            return encode_for_multisigning(
                self.decoded_transaction, self.signed_by_account()
            )
        else:
            return encode_for_signing(self.decoded_transaction)

    def __str__(self) -> str:
        return json.dumps(
            {
                "signedBy": self.signed_by_account(),
                "signatureValid": self.is_valid(),
                "signatureMultiSign": self.is_multisigned(),
            }
        )
