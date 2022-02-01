from importlib.resources import path
from pathlib import Path
import json
import requests
from xrplpers.verification import TransactionVerifier
import sys

py_version = sys.version_info
if py_version.major == 3 and py_version.minor >= 9:
    from functools import cache
else:
    from functools import lru_cache as cache
from os import environ


@cache
def get_creds(path: Path = None):
    if path:
        creds = path
    elif environ.get("XUMM_CREDS_PATH"):
        creds = Path(environ.get("XUMM_CREDS_PATH"))
    else:
        creds = Path("creds.json")
    return json.loads(creds.read_text())


def verify_signature(payload):

    uuid = payload["payloadResponse"]["payload_uuidv4"]
    url = f"https://xumm.app/api/v1/platform/payload/{uuid}"
    headers = {"Accept": "application/json", "authorization": "Bearer"}
    headers.update(get_creds())
    response = requests.request("GET", url, headers=headers)
    tx_data = response.json()
    verifier = TransactionVerifier(tx_data["response"]["hex"])
    if not verifier.is_valid():
        return False
    return tx_data["response"]["account"]


def xumm_login(user=None):
    xumm_payload = {
        "options": {
            "submit": False,
            "expire": 240,
        },
    }
    if user:
        xumm_payload["user_token"] = user
    response = submit_xumm_transaction({"TransactionType": "SignIn"}, **xumm_payload)
    return response.json()


def submit_xumm_transaction(transaction, **kwargs):
    url = "https://xumm.app/api/v1/platform/payload"
    headers = {"Accept": "application/json", "authorization": "Bearer"}
    headers.update(get_creds())
    xumm_payload = kwargs
    xumm_payload["txjson"] = transaction

    response = requests.request("POST", url, headers=headers, json=xumm_payload)
    response.raise_for_status()
    return response


def get_xumm_transaction(uuid):
    url = f"https://xumm.app/api/v1/platform/payload/{uuid}"
    headers = {"Accept": "application/json", "authorization": "Bearer"}
    headers.update(get_creds())
    response = requests.get(url, headers=headers)
    return response.json()
