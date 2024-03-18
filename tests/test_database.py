from api_adapter.database import (
    create_invoice_count,
    delete_invoice,
    get_user,
    login_user,
    logout_user,
    register_user,
    store_invoice,
)
from tests.conftest import cleanup

test_user_data = {
    "email": "test@email.com",
    "firstname": "test",
    "lastname": "email",
    "password": "somepassword",
}


def test_get_user(db):
    cleanup(db, test_user_data["email"])
    register_user(test_user_data)
    user = get_user(test_user_data["email"])

    assert user["email"] == test_user_data["email"]
    assert user["password"] == test_user_data["password"]

    cleanup(db, test_user_data["email"])


def test_get_user_not_registered(db):
    test_email = "notregistered@email.com"
    cleanup(db, test_email)
    user = get_user(test_email)

    assert user is None


def test_register_user(db):
    users = db["users"]
    cleanup(db, test_user_data["email"])
    query = {"email": test_user_data["email"]}

    assert users.find_one(query) is None

    response = register_user(test_user_data)

    assert users.find_one(query) is not None
    assert response[0] == f"User {test_user_data['email']} registered"

    cleanup(db, test_user_data["email"])


def test_login_user(db):
    users = db["users"]
    logged_in = db["logged_in"]
    query = {"email": test_user_data["email"]}

    # Register but not logged in
    cleanup(db, test_user_data["email"])
    _ = register_user(test_user_data)

    assert users.find_one(query) is not None
    assert logged_in.find_one(query) is None

    token, msg = login_user(test_user_data["email"], test_user_data["password"])
    logged_in_user = logged_in.find_one(query)

    assert token is not None
    assert logged_in_user["token"] == token
    assert msg == f"{logged_in_user['email']} is now logged in"
    assert logged_in_user["email"] == test_user_data["email"]


def test_login_user_wrong_password(db):
    users = db["users"]
    logged_in = db["logged_in"]
    query = {"email": test_user_data["email"]}
    cleanup(db, test_user_data["email"])
    _ = register_user(test_user_data)

    assert users.find_one(query) is not None
    assert logged_in.find_one(query) is None

    token, msg = login_user(test_user_data["email"], "incorrect password")

    assert token is None
    assert msg == f"Password incorrect for {test_user_data['email']}"
    assert logged_in.find_one(query) is None
    cleanup(db, test_user_data["email"])


def test_login_user_not_registered(db):
    users = db["users"]
    logged_in = db["logged_in"]
    query = {"email": test_user_data["email"]}
    cleanup(db, test_user_data["email"])
    assert users.find_one(query) is None
    token, msg = login_user(test_user_data["email"], test_user_data["password"])

    assert token is None
    assert msg == f"{test_user_data['email']} is not a registered user"
    assert logged_in.find_one(query) is None
    cleanup(db, test_user_data["email"])


def test_login_user_already_logged_in(db):
    users = db["users"]
    logged_in = db["logged_in"]
    query = {"email": test_user_data["email"]}

    # Register but not logged in
    cleanup(db, test_user_data["email"])
    _ = register_user(test_user_data)

    assert users.find_one(query) is not None
    assert logged_in.find_one(query) is None

    token0, msg0 = login_user(test_user_data["email"], test_user_data["password"])
    logged_in_user = logged_in.find_one(query)

    assert token0 is not None
    assert msg0 == f"{test_user_data['email']} is now logged in"
    assert logged_in_user["token"] == token0
    assert logged_in_user["email"] == test_user_data["email"]

    token1, msg1 = login_user(test_user_data["email"], test_user_data["password"])
    logged_in_user = logged_in.find_one(query)

    assert token1 is not None
    assert msg1 == f"{test_user_data['email']} is now logged in"
    assert token0 == token1
    assert logged_in_user["email"] == test_user_data["email"]
    cleanup(db, test_user_data["email"])


def test_logout_user(db):
    users = db["users"]
    logged_in = db["logged_in"]
    cleanup(db, test_user_data["email"])
    query = {"email": test_user_data["email"]}
    _ = register_user(test_user_data)

    assert users.find_one(query) is not None
    assert logged_in.find_one(query) is None

    token0, msg = login_user(test_user_data["email"], test_user_data["password"])
    logged_in_user = logged_in.find_one(query)

    assert token0 is not None
    assert msg == f"{logged_in_user['email']} is now logged in"
    assert logged_in_user["token"] == token0
    assert logged_in_user["email"] == test_user_data["email"]

    logout_user(test_user_data["email"], token0)

    logged_in_user = logged_in.find_one(query)

    assert logged_in_user is None
    cleanup(db, test_user_data["email"])


def test_logout_user_failed(db):
    users = db["users"]
    logged_in = db["logged_in"]
    cleanup(db, test_user_data["email"])
    query = {"email": test_user_data["email"]}
    _ = register_user(test_user_data)

    assert users.find_one(query) is not None
    assert logged_in.find_one(query) is None

    token0, msg0 = login_user(test_user_data["email"], test_user_data["password"])
    logged_in_user = logged_in.find_one(query)

    assert token0 is not None
    assert logged_in_user["token"] == token0
    assert logged_in_user["email"] == test_user_data["email"]

    logout_user(test_user_data["email"], "not a real token")

    logged_in_user = logged_in.find_one(query)

    assert logged_in_user["token"] == token0
    assert logged_in_user["email"] == test_user_data["email"]
    cleanup(db, test_user_data["email"])


def test_store_invoice(db):
    users = db["users"]
    cleanup(db, test_user_data["email"])
    query = {"email": test_user_data["email"]}

    # Register and login test user
    _ = register_user(test_user_data)
    token, _ = login_user(test_user_data["email"], test_user_data["password"])

    user = users.find_one(query)

    assert user["invoices"] == []

    msg = store_invoice(token, "somestring", "created")
    user = users.find_one(query)

    assert msg == f"Successfully stored invoice for {test_user_data['email']}"
    assert len(user["invoices"]) == 1
    assert user["invoices"][0]["content"] == "somestring"
    assert user["invoices"][0]["method"] == "created"

    msg = store_invoice(token, "some other string", "received", "received_timestamp")
    user = users.find_one(query)

    assert msg == f"Successfully stored invoice for {test_user_data['email']}"
    assert len(user["invoices"]) == 2
    assert user["invoices"][1]["content"] == "some other string"
    assert user["invoices"][1]["method"] == "received"


def test_delete_invoice(db):
    users = db["users"]
    cleanup(db, test_user_data["email"])
    query = {"email": test_user_data["email"]}

    # Register and login test user
    _ = register_user(test_user_data)
    token, _ = login_user(test_user_data["email"], test_user_data["password"])

    user = users.find_one(query)
    assert user["invoices"] == []
    invoice_id = db["invoice_id"].find_one()["invoice_id"]

    store_invoice(token, "somestring", "created")
    user = users.find_one(query)
    assert len(user["invoices"]) == 1
    assert user["invoices"][0]["invoice_id"] == invoice_id

    store_invoice(token, "somestring2", "created")
    user = users.find_one(query)
    invoice_id_two = user["invoices"][1]["invoice_id"]

    delete_first = delete_invoice(token, invoice_id)
    user = users.find_one(query)
    assert delete_first == f"Successfully deleted invoice {invoice_id}"
    assert len(user["invoices"]) == 1

    delete_second = delete_invoice(token, invoice_id_two)
    assert delete_second == f"Successfully deleted invoice {invoice_id_two}"
    user = users.find_one(query)
    assert len(user["invoices"]) == 0


def test_invoice_count(db):
    cleanup(db, test_user_data["email"])
    assert create_invoice_count() == "Counter exists"
