"""
Users functionality
"""

from api_adapter.database import get_list_users


def list_users() -> dict:
    return get_list_users()
