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
    response = call_xumm_api(url)
    tx_data = response
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
    return response


def submit_xumm_transaction(transaction, **kwargs):
    url = "https://xumm.app/api/v1/platform/payload"
    xumm_payload = kwargs
    xumm_payload["txjson"] = transaction
    return call_xumm_api(url, payload=xumm_payload, method="POST")


def get_xumm_transaction(uuid):
    url = f"https://xumm.app/api/v1/platform/payload/{uuid}"
    return call_xumm_api(url)


def call_xumm_api(url, payload=None, method="GET"):
    headers = {"Accept": "application/json", "authorization": "Bearer"}
    headers.update(get_creds())
    if payload:
        response = requests.request(method, url, headers=headers, json=payload)
    else:
        response = requests.request(method, url, headers=headers)
    response.raise_for_status()
    return response.json()
