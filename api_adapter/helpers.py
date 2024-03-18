import logging
from datetime import datetime
from hashlib import md5
from uuid import uuid4

import xmltodict
from pytz import timezone


def get_customer_name(invoice: str) -> str:
    try:
        invoice_dict = xmltodict.parse(invoice)
    except Exception:
        return "NOT FOUND"
    customer_party = invoice_dict["Invoice"]["cac:AccountingCustomerParty"]
    try:
        name = customer_party["cac:Party"]["cac:PartyName"]["cbc:Name"]
    except KeyError:
        name = customer_party["cac:Party"]["cac:PartyLegalEntity"][
            "cbc:RegistrationName"
        ]

    if name is None:
        logging.error("Can't find name in ubl, defaulting to NOT FOUND")
        name = "NOT FOUND"

    return name


def generate_token() -> str:
    return str(uuid4())


def encrypt_password(password):
    return md5(password.encode()).hexdigest()


def get_time_string() -> str:
    sydney_tz = timezone("Australia/Sydney")
    return datetime.now(sydney_tz).strftime("%d/%m/%Y, %H:%M:%S")


def get_time() -> datetime:
    sydney_tz = timezone("Australia/Sydney")
    return datetime.now(sydney_tz)
