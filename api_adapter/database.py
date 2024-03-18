import logging
import random
import sys
from typing import Optional, Tuple

from pymongo import MongoClient

from api_adapter.constants import DB_CLIENT_PREFIX, ENVOY, hex_colors
from api_adapter.helpers import generate_token, get_customer_name, get_time_string


def connect_to_db():
    """
    Connect to db
    """
    client = MongoClient(f"{DB_CLIENT_PREFIX}{ENVOY}?retryWrites=true&w=majority")
    return client[ENVOY]


def create_invoice_count():
    db = connect_to_db()
    if not db["invoice_id"].find_one():
        invoice_id = {"invoice_id": 0}
        db["invoice_id"].insert_one(invoice_id)
        return "Invoice Id counter added"
    else:
        return "Counter exists"


def get_user(email: str) -> Optional[dict]:
    """
    Searches users db to find user information using an email
    """
    db = connect_to_db()
    users = db["users"]
    return users.find_one({"email": email})


def get_email_from_token(token: str) -> str:
    """
    Given a token return that users email
    """
    db = connect_to_db()
    logged_in = db["logged_in"]
    logged_in_query = {"token": token}
    user = logged_in.find_one(logged_in_query)
    if user is None:
        return "Invalid token"
    return user["email"]


def get_user_from_token(token: str) -> dict:
    """
    Given a token return a user
    """
    db = connect_to_db()
    logged_in = db["logged_in"]
    query = {"token": token}
    user = logged_in.find_one(query)
    users_collection = db["users"]
    query = {"email": user["email"]}
    user = users_collection.find_one(query)
    return user


def check_registered(email):
    """
    Given an email, check if it belongs to a registered user
    """
    if email is None:
        return False

    db = connect_to_db()
    users = db["users"]
    query = {"email": email}
    user = users.find_one(query)

    return True if user is not None else False


def get_list_users() -> dict:
    """
    List all registered users in the database
    """
    db = connect_to_db()
    users = db["users"]
    users_list = list(users.find({}))
    response = {"users": []}
    for user in users_list:
        response["users"].append(
            {
                "email": user["email"],
                "firstname": user["firstname"],
                "lastname": user["lastname"],
                "num_invoices": len(user["invoices"]),
            }
        )
    return response


def check_logged_in_email(email: str = None):
    """
    Given an email, check if it belongs to a logged in user
    """
    if email is None:
        return False

    db = connect_to_db()
    logged_in = db["logged_in"]
    query = {"email": email}
    user = logged_in.find_one(query)

    return True if user is not None else False


def check_logged_in_token(
    token: str = None,
):
    """
    Given a token, check if it belongs to a logged in user
    """
    if token is None:
        return False

    db = connect_to_db()
    logged_in = db["logged_in"]
    query = {"token": token}
    user = logged_in.find_one(query)

    return True if user is not None else False


def register_user(user_data: dict) -> str:
    """
    Creates document in db containing users information including hashed password, returning a generated token
    """
    db = connect_to_db()

    email = user_data["email"]
    user_data["invoices"] = []
    print(user_data)

    users = db["users"]
    users.insert_one(user_data)

    hex_color = get_user_profile_color(email)

    return (f"User {email} registered", hex_color)


def login_user(email: str, password: str) -> str:
    """
    Generates new token for user and saves to db and returns
    """
    db = connect_to_db()
    users = db["users"]
    query = {"email": email}

    user = users.find_one(query)

    if user is not None:
        if user["password"] != password:
            logging.error(f"Password incorrect for {email}")
            return None, f"Password incorrect for {email}"

        logged_in = db["logged_in"]
        logged_in_user = logged_in.find_one(query)

        if logged_in_user is not None and logged_in_user["email"] == email:
            existing_token = logged_in_user["token"]
            return existing_token, f"{email} is now logged in"

        token = generate_token()
        logged_in.insert_one({"email": email, "token": token})

        return token, f"{email} is now logged in"
    logging.error(f"{email} is not a registered user")
    return None, f"{email} is not a registered user"


def logout_user(email: str, token: str) -> str:
    """
    Remove logged in entry from db
    """
    db = connect_to_db()
    logged_in = db["logged_in"]

    query = {"email": email}

    logged_in_user = logged_in.find_one(query)
    if logged_in_user is None:
        logging.error(f"{email} is not logged in")
        return f"{email} is not logged in"
    if logged_in_user["token"] != token:
        logging.error(f"{token} doesn't belong to {email}")
        return f"{token} doesn't belong to {email}"

    logged_in.delete_one(query)
    return f"Successfully logged out {email}"


def store_invoice(
    token: str, invoice: str, method: str, received_timestamp: str = ""
) -> str:
    db = connect_to_db()
    logged_in = db["logged_in"]
    logged_in_query = {"token": token}

    logged_in_user = logged_in.find_one(logged_in_query)
    if logged_in_user is None:
        logging.error("Need to login to store an invoice")
        return "Need to login to store an invoice"

    users = db["users"]
    users_query = {"email": logged_in_user["email"]}

    customer_name = get_customer_name(invoice)

    invoice_id = db["invoice_id"].find_one()["invoice_id"]

    invoice_data = {
        "invoice_id": invoice_id,
        "customer_name": customer_name,
        "timestamp": get_time_string(),
        "size": sys.getsizeof(invoice),
        "content": invoice,
        "method": method,
    }

    if method == "received":
        invoice_data["received_timestamp"] = received_timestamp

    db["invoice_id"].update_one(
        {"invoice_id": invoice_id}, {"$set": {"invoice_id": invoice_id + 1}}
    )

    users.update_one(users_query, {"$push": {"invoices": invoice_data}})
    return f"Successfully stored invoice for {logged_in_user['email']}"


def get_invoices(token: str) -> Tuple[list, str]:
    db = connect_to_db()
    logged_in = db["logged_in"]
    logged_in_query = {"token": token}

    logged_in_user = logged_in.find_one(logged_in_query)
    if logged_in_user is None:
        logging.error("Need to login to get invoices")
        return ([], "Need to login to get invoices")
    users = db["users"]
    users_query = {"email": logged_in_user["email"]}

    user = users.find_one(users_query)
    created = []
    received = []
    for invoice in user["invoices"]:
        if invoice["method"] == "created":
            created.append(invoice)
        elif invoice["method"] == "received":
            received.append(invoice)
    return (
        {"created": created, "received": received},
        f"Successfully retreived invoices for {logged_in_user['email']}",
    )


def get_user_profile_color(email: str) -> str:
    db = connect_to_db()
    users = db["users"]

    query = {"email": email}
    user = users.find_one(query)

    try:
        hex_color = user["hex_color"]
    except Exception:
        hex_color = random.choice(hex_colors)
        users.update_one(query, {"$set": {"hex_color": str(hex_color)}})

    return hex_color


def get_user_first_last_name(email: str) -> Tuple[str]:
    db = connect_to_db()
    users = db["users"]

    query = {"email": email}
    user = users.find_one(query)

    if user is None:
        return ("", "")

    return ("valid email", user["firstname"], user["lastname"])


def update_user_profile_color(email: str, new_color: str) -> str:
    db = connect_to_db()
    users = db["users"]
    query = {"email": email}

    user = users.find_one(query)

    if user is not None:
        users.update_one(query, {"$set": {"hex_color": new_color}})
        return "profile colour successfully updated"

    logging.error(f"{email} is not a registered user")
    return f"{email} is not a registered user"


def update_user_profile_firstname(email: str, new_firstname: str) -> str:
    db = connect_to_db()
    users = db["users"]
    query = {"email": email}

    user = users.find_one(query)

    if user is not None:
        users.update_one(query, {"$set": {"firstname": new_firstname}})
        return f"firstname successfully updated for ${email}"

    logging.error(f"{email} is not a registered user")
    return f"{email} is not a registered user"


def update_user_profile_lastname(email: str, new_lastname: str) -> str:
    db = connect_to_db()
    users = db["users"]
    query = {"email": email}

    user = users.find_one(query)

    if user is not None:
        users.update_one(query, {"$set": {"lastname": new_lastname}})
        return f"lastname successfully updated for ${email}"

    logging.error(f"{email} is not a registered user")
    return f"{email} is not a registered user"


def update_user_password(email: str, password: str, new_password: str) -> str:
    db = connect_to_db()
    users = db["users"]
    query = {"email": email}

    user = users.find_one(query)

    if user is not None:
        if user["password"] != password:
            logging.error(f"Password incorrect for {email}")
            return f"Password incorrect for {email}"

        if user["password"] == password:
            users.update_one(query, {"$set": {"password": new_password}})
            return "Password successfully updated"

    logging.error(f"{email} is not a registered user")
    return f"{email} is not a registered user"


def register_team(team_name: str, owner: dict) -> str:
    db = connect_to_db()
    teams = db["teams"]
    query = {"team_name": team_name}
    team = teams.find_one(query)
    if team is not None:
        logging.error(f"{team_name} is already a registered team")
        return f"{team_name} is already a registered team"

    owner = {
        "email": owner["email"],
        "role": "Owner",
        "time_joined": get_time_string(),
    }

    team = {
        "team_name": team_name,
        "time_created": get_time_string(),
        "team_owner": owner,
        "members": [],
    }

    team["members"].append(owner)
    teams.insert_one(team)
    _ = update_user_team(team_name, owner["email"])
    return f"{team_name} successfully created."


def add_user_to_team(team_name: str, invitee_email: str, role: str) -> str:
    db = connect_to_db()
    teams = db["teams"]
    query = {"team_name": team_name}
    team = teams.find_one(query)
    if team is None:
        logging.error(f"{team_name} does not exist")
        return f"{team_name} does not exist"

    user = get_user(invitee_email)
    if user is None:
        logging.error(f"{invitee_email} does not exist")
        return f"{invitee_email} does not exist"

    if any(member["email"] == invitee_email for member in team["members"]):
        logging.error(f"{invitee_email} is already in this team")
        return f"{invitee_email} is already in this team"

    member = {
        "email": user["email"],
        "role": role,
        "time_joined": get_time_string(),
    }
    teams.update_one(query, {"$push": {"members": member}})

    _ = update_user_team(team_name, invitee_email)
    return f"{invitee_email} successfully added to {team_name} as a{' ' + role if role == 'Member' else 'n ' + role}"


def is_member_of(token: str) -> bool:
    user = get_user_from_token(token)
    _, members = get_members_of(user["team"])
    if any(member["email"] == user["email"] for member in members):
        return True
    return False


def get_members_of(team_name: str, role: str = None) -> Tuple[str, list]:
    db = connect_to_db()
    teams = db["teams"]
    query = {"team_name": team_name}
    team = teams.find_one(query)
    if team is None:
        logging.error(f"{team_name} does not exist")
        return f"{team_name} does not exist", []

    users = db["users"]
    members = []
    if role is None:

        for member in team["members"]:
            query = {"email": member["email"]}
            user = users.find_one(query)
            members.append(
                {
                    "email": user["email"],
                    "firstname": user["firstname"],
                    "lastname": user["lastname"],
                    "invoices": user["invoices"],
                    "hex_color": user["hex_color"],
                    "role": member["role"],
                    "team": user["team"],
                    "time_joined": member["time_joined"],
                }
            )

        return f"Successfully got list of members in {team_name}", members

    for member in team["members"]:
        query = {"email": member["email"]}
        if member["role"] == role:
            user = users.find_one(query)
            members.append(
                {
                    "email": user["email"],
                    "firstname": user["firstname"],
                    "lastname": user["lastname"],
                    "invoices": user["invoices"],
                    "hex_color": user["hex_color"],
                    "role": member["role"],
                    "team": user["team"],
                    "time_joined": member["time_joined"],
                }
            )

    return f"Successfully got list of members in {team_name} with role {role}", members


def update_user_team(team_name: str, email: str) -> str:
    db = connect_to_db()
    users = db["users"]
    query = {"email": email}
    users.update_one(query, {"$set": {"team": team_name}})
    logging.info(f"Updating {email}'s team to {team_name}")


def db_cleanup() -> Tuple[int, int]:
    db = connect_to_db()
    users = db["users"]
    logged_in = db["logged_in"]

    users_data = users.delete_many({})
    logging.info(f"Removed {users_data.deleted_count} documents from users collection")
    logged_in_data = logged_in.delete_many({})
    logging.info(
        f"Removed {logged_in_data.deleted_count} documents from logged_in collection"
    )
    return users_data.deleted_count, logged_in_data.deleted_count


def delete_invoice(token: str, invoice_id: int):
    """
    Delete invoice instance by invoice_id
    """
    db = connect_to_db()
    logged_in = db["logged_in"]
    logged_in_query = {"token": token}

    logged_in_user = logged_in.find_one(logged_in_query)
    if logged_in_user is None:
        logging.error("Need to login to delete invoice")
        return ([], "Need to login to delete invoice")

    users = db["users"]
    users_query = {"email": logged_in_user["email"]}
    user = users.find_one(users_query)
    _id = user["_id"]

    db.users.update_many(
        {"_id": _id}, {"$pull": {"invoices": {"invoice_id": invoice_id}}}
    )

    users = db["users"]
    users_query = {"email": logged_in_user["email"]}
    user = users.find_one(users_query)

    return f"Successfully deleted invoice {invoice_id}"
