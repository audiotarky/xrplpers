from pathlib import Path
import json
import requests
from xrplpers.verification import TransactionVerifier


def verify_signature(payload):
    uuid = payload["payloadResponse"]["payload_uuidv4"]
    url = f"https://xumm.app/api/v1/platform/payload/{uuid}"
    creds = Path("creds.json")
    headers = {"Accept": "application/json", "authorization": "Bearer"}
    headers.update(json.loads(creds.read_text()))
    response = requests.request("GET", url, headers=headers)
    tx_data = response.json()
    verifier = TransactionVerifier(tx_data["response"]["hex"])
    if not verifier.is_valid():
        return False
    return tx_data["response"]["account"]


def xumm_login(user=None):
    creds = Path("creds.json")
    url = "https://xumm.app/api/v1/platform/payload"
    headers = {"Accept": "application/json", "authorization": "Bearer"}
    headers.update(json.loads(creds.read_text()))
    xumm_payload = {
        "options": {
            "submit": False,
            "expire": 240,
        },
        "txjson": {"TransactionType": "SignIn"},
    }
    if user:
        xumm_payload["user_token"] = user
    response = requests.request("POST", url, headers=headers, json=xumm_payload)
    try:
        response.raise_for_status()
        return response.json()
    except:
        return {}
