"""
Functionality that is behind the "create" endpoint. This:
    - creates and validates the invoice via an API
    - stores the invoice in mongoDB
"""

from typing import Optional

import requests

from api_adapter.constants import INVOICE_CREATE_URL
from api_adapter.database import store_invoice


def persist_invoice(token: str, invoice_details: dict) -> dict:
    """
    Create and store invoice in mongodb
    """
    response = create_invoice(invoice_details)
    if response is None:
        return {"msg": "Could not create and save invoice."}
    msg = store_invoice(token, response.text, "created")
    return {"msg": msg}


def create_invoice(invoice_details: dict) -> Optional[dict]:
    """
    Calls create_invoice API that a different group made
    to create an invoice given some json data.
    """
    data = dict(invoice_details)
    response = requests.post(INVOICE_CREATE_URL, json=data)
    if response.status_code == 200:
        return response
    return None
