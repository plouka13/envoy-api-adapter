"""
Functionality that is behind the "listing" endpoint. This:
    - gets all the invoices that the user has uploaded
"""

from api_adapter.database import get_invoices
from api_adapter.receive import update_received


def list_invoices(token: str) -> dict:
    """
    Gets a list of all invoices the user has uploaded
    """
    update_received(token)

    invoices, msg = get_invoices(token)
    return {
        "msg": msg,
        "created_invoices": invoices["created"],
        "received_invoices": invoices["received"],
    }
