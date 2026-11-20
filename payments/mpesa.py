import base64, requests
from datetime import datetime
from django.conf import settings

BASE = "https://sandbox.safaricom.co.ke"   # change to https://api.safaricom.co.ke for live

def get_token():
    r = requests.get(
        f"{BASE}/oauth/v1/generate?grant_type=client_credentials",
        auth=(settings.MPESA["CONSUMER_KEY"], settings.MPESA["CONSUMER_SECRET"]),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def stk_push(phone, amount):
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    shortcode = settings.MPESA["SHORTCODE"]
    password = base64.b64encode(
        f"{shortcode}{settings.MPESA['PASSKEY']}{ts}".encode()
    ).decode()
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": ts,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA["CALLBACK_URL"],
        "AccountReference": "MiniShop",
        "TransactionDesc": "Mini project payment",
    }
    r = requests.post(
        f"{BASE}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {get_token()}"},
        timeout=30,
    )
    return r.json()