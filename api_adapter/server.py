"""
Endpoints that allows for the user to use the buttons:
    - create
    - render
    - send
    - delete
    - login
    - log out
    - send
    - sign up
"""

import json
import logging

from flask import Flask, request
from flask_cors import CORS

from api_adapter.auth import login, logout, signup
from api_adapter.create import persist_invoice
from api_adapter.database import check_logged_in_token, db_cleanup, delete_invoice
from api_adapter.listing import list_invoices
from api_adapter.profile import (
    profile_details,
    reset_password,
    update_profile_colour,
    update_profile_firstname,
    update_profile_lastname,
)
from api_adapter.render import get_render
from api_adapter.send import send_invoice
from api_adapter.stats import (
    curr_daily_stats,
    curr_month_stats,
    curr_year_stats,
    last_thirty_days_stats,
    num_created_stats,
    num_received_stats,
    num_sent_stats,
)
from api_adapter.team import create_team, invite_member, list_team_members
from api_adapter.users import list_users

APP = Flask(__name__)
CORS(APP)

EMPTY_BODY_STRING = "YOU'VE GIVEN ME AN EMPTY BODY :("


@APP.route("/")
def default_route():
    return "Hello, World!"


@APP.route("/signup", methods=["POST"])
def signup_route():
    body = request.get_json()
    print(body)
    if (
        "email" not in body
        or "password" not in body
        or "firstname" not in body
        or "lastname" not in body
    ):
        return {"msg": "Needs email, password, firstname and lastname in body"}
    response = signup(body)
    logging.info(response)
    return response


@APP.route("/login", methods=["POST"])
def login_route():
    body = request.get_json()
    if "email" not in body or "password" not in body:
        return {"msg": "Needs email and password in body"}
    response = login(body)
    logging.info(response)
    return response


@APP.route("/logout", methods=["POST"])
def logout_route():
    body = request.get_json()
    if "token" not in body or "email" not in body:
        return {"msg": "Needs email and token in body"}
    response = logout(body)
    logging.info(response)
    return response


@APP.route("/user/details", methods=["POST"])
def user_details_route():
    body = request.get_json()
    if "email" not in body:
        return {"msg": "Needs email in body"}
    response = profile_details(body)
    logging.info(response)
    return response


@APP.route("/user/update/color", methods=["POST"])
def update_color_route():
    body = request.get_json()
    if "email" not in body:
        return {"msg": "Needs email in body"}
    response = update_profile_colour(body)
    logging.info(response)
    return response


@APP.route("/user/update/firstname", methods=["POST"])
def update_firstname_route():
    body = request.get_json()
    if "email" not in body:
        return {"msg": "Needs email in body"}
    response = update_profile_firstname(body)
    logging.info(response)
    return response


@APP.route("/user/update/lastname", methods=["POST"])
def update_lastname_route():
    body = request.get_json()
    if "email" not in body:
        return {"msg": "Needs email in body"}
    response = update_profile_lastname(body)
    logging.info(response)
    return response


@APP.route("/user/update/password", methods=["POST"])
def update_password_route():
    body = request.get_json()
    if "password" not in body or "new_password" not in body:
        return {"msg": "Needs password in body"}
    response = reset_password(body)
    logging.info(response)
    return response


@APP.route("/invoice/send", methods=["POST"])
def send_route():
    body = request.get_json()
    response = send_invoice(body)
    logging.info(response)
    return response


@APP.route("/invoice/create", methods=["POST"])
def create_route():
    body = request.get_json()
    logging.error(body)
    if "token" not in body or "invoice_data" not in body:
        return {"msg": "Needs token and invoice_data"}
    response = persist_invoice(body["token"], body["invoice_data"])
    logging.info(response)
    return json.dumps(response)


@APP.route("/invoice/list", methods=["GET"])
def list_invoices_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = list_invoices(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/invoice/render", methods=["POST"])
def render_invoice_route():
    token = request.headers.get("token")
    address = request.headers.get("invoice_id")
    if token is None or address is None:
        return {"msg": "Needs token and invoice_id in headers"}
    response = get_render(token, address)
    logging.info(response)
    return json.dumps(response)


@APP.route("/invoice/delete", methods=["DELETE"])
def delete_invoice_route():
    token = request.headers.get("token")
    invoice_id = request.headers.get("invoice_id")
    if token is None or invoice_id is None:
        return {"msg": "Needs token and invoice_id in headers"}
    response = delete_invoice(token, int(invoice_id))
    logging.info(response)
    return json.dumps(response)


@APP.route("/users/list", methods=["GET"])
def list_users_route():
    token = request.headers.get("token")
    if not check_logged_in_token(token):
        return {"msg": "Invalid token"}
    response = list_users()
    logging.info(response)
    return json.dumps(response)


@APP.route("/team/create", methods=["POST"])
def team_create_route():
    token = request.headers.get("token")
    if not check_logged_in_token(token):
        return {"msg": "Invalid token"}
    body = request.get_json()
    if "team_name" not in body:
        return {"msg": "Needs team_name in the body."}
    response = create_team(token, body["team_name"])
    logging.info(response)
    return response


@APP.route("/team/invite", methods=["POST"])
def team_invite_route():
    token = request.headers.get("token")
    if not check_logged_in_token(token):
        return {"msg": "Invalid token"}
    body = request.get_json()
    role = "Member"
    if "team_name" not in body:
        return {"msg": "Needs team_name in the body."}
    elif "invitee_email" not in body:
        return {"msg": "Needs invitee_email in the body."}
    elif "role" in body:
        role = body["role"]

    response = invite_member(body["team_name"], body["invitee_email"], role)

    logging.info(response)
    return response


@APP.route("/team/members", methods=["GET"])
def team_members_route():
    token = request.headers.get("token")
    if not check_logged_in_token(token):
        return {"msg": "Invalid token"}
    role = request.args.get("role")
    response = list_team_members(token, role)

    logging.info(response)
    return json.dumps(response)


@APP.route("/stats/sent", methods=["GET"])
def sent_stats_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = num_sent_stats(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/stats/received", methods=["GET"])
def received_stats_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = num_received_stats(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/stats/day", methods=["GET"])
def daily_stats_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = curr_daily_stats(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/stats/created", methods=["GET"])
def create_stats_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = num_created_stats(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/stats/month", methods=["GET"])
def month_stats_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = curr_month_stats(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/stats/year", methods=["GET"])
def year_stats_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = curr_year_stats(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/stats/thirtydays", methods=["GET"])
def thirty_daily_stats_route():
    token = request.headers.get("token")
    if token is None:
        return {"msg": "Needs token in headers"}
    response = last_thirty_days_stats(token)
    logging.info(response)
    return json.dumps(response)


@APP.route("/test", methods=["POST"])
def test_route():
    body = request.get_json()
    return body


@APP.route("/cleanup", methods=["POST"])
def cleanup_route():
    # DEV ONLY ROUTE SHOULD
    # FIND A WAY TO REMOVE IN PROD
    users_val, logged_in_val = db_cleanup()
    res = {
        # "msg": f"Removed #{users_val} entries from users and #{logged_in_val} entries from logged_in."
        "msg": "Removed #{users_val} entries from users and #{logged_in_val} entries from logged_in."
    }
    return res
