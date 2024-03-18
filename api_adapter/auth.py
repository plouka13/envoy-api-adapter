"""
Functionality that allows for the user to:
    - sign up
    - log in
    - log out
"""

import logging
import re

from api_adapter.database import get_user, login_user, logout_user, register_user
from api_adapter.helpers import encrypt_password


def signup(user_data: dict) -> dict:
    """
    Signs up the user given some data about the user.

        Parameters:
            user_data: dict = {
                "email": "",
                "password": "",
                "firstname": "",
                "lastname": ""
            }

        Returns:
            data: dict = {
                message: string
                token: string
                hex_color: string
            }

    """
    if not valid_email(user_data["email"]):
        return {"msg": f"{user_data['email']} is not a valid email"}

    if get_user(user_data["email"]):
        logging.error(
            f"An account with email: {user_data['email']} is already registered"
        )
        return {
            "msg": f"An account with email: {user_data['email']} is already registered"
        }

    if not valid_password(user_data["password"]):
        return {
            "msg": "Password needs to contain at least 6 characters, 1 capital letter, 1 lowercase letter and 1 number"
        }

    if not valid_name(user_data["firstname"]) and user_data["lastname"]:
        return {"msg": "First and Last names must not be empty"}

    user_data["password"] = encrypt_password(user_data["password"])
    msg, hex_color = register_user(user_data)
    if msg != f"User {user_data['email']} registered":
        return {"msg": msg, "token": None}

    token, _ = login_user(user_data["email"], user_data["password"])

    if token is not None:
        msg += " and logged in"
    return {"msg": msg, "token": token, "hex_color": hex_color}


def login(credentials: dict) -> dict:
    """
    Logs the user into their account given a username and password and returns a token.

        Parameters:
            credentials: dict = {
                "email": string,
                "password": string
            }

        Returns:
            data: dict = {
                "message": string,
                "token": string
            }
    """
    if not valid_email(credentials["email"]):
        return {"msg": f"{credentials['email']} is not a valid email"}

    encrypted_password = encrypt_password(credentials["password"])

    token, msg = login_user(credentials["email"], encrypted_password)

    return {"msg": msg, "token": token}


def logout(data: dict) -> dict:
    """
    Logs the user out of their account given a token and returns a msg.

        Parameters:
            data: dict = {
                "token": string
                "email": string
            }

        Returns:
            response: dict = {
                "message": string
            }
    """
    msg = logout_user(data["email"], data["token"])
    return {"msg": msg}


def valid_email(email: str) -> bool:
    """
    Validates Email given
    """
    email_regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    return True if re.search(email_regex, email) else False


def valid_password(password: str) -> bool:
    """
    Validates password given
    """
    if (
        any(x.isupper() for x in password)
        and any(x.islower() for x in password)
        and any(x.isdigit() for x in password)
        and len(password) >= 6
    ):
        return True
    return False


def valid_name(name: str) -> bool:
    """
    Validates name given
    """
    return len(name) >= 1
