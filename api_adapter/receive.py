import logging

import requests

from api_adapter.constants import INVOICE_RECEIVING_URL
from api_adapter.database import get_email_from_token, store_invoice


def update_received(token: str) -> None:
    """
    Update the received invoices for a user.
    """
    email = get_email_from_token(token)
    headers = {"email": email}
    res = requests.get(INVOICE_RECEIVING_URL, headers=headers)
    if res.ok:
        for invoice in res.json()["invoices"]:
            msg = store_invoice(
                token=token,
                invoice=invoice["content"],
                method="received",
                received_timestamp=invoice["time_received"],
            )
            logging.info(msg)
