import pytest

from api_adapter.auth import (
    login,
    logout,
    signup,
    valid_email,
    valid_name,
    valid_password,
)
from api_adapter.database import connect_to_db


def cleanup(db, email):
    users = db["users"]
    logged_in = db["logged_in"]

    users.delete_one({"email": email})
    logged_in.delete_one({"email": email})


@pytest.fixture
def db():
    return connect_to_db()


@pytest.fixture
def test_user_data():
    return {
        "email": "test@email.com",
        "firstname": "Test",
        "lastname": "Email",
        "password": "SomePassword123",
    }


def test_signup(db, test_user_data):
    users_collection = db["users"]
    logged_in_collection = db["logged_in"]
    cleanup(db, test_user_data["email"])
    query = {"email": test_user_data["email"]}

    assert users_collection.find_one(query) is None
    assert logged_in_collection.find_one(query) is None

    result = signup(test_user_data)

    assert users_collection.find_one(query) is not None
    assert logged_in_collection.find_one(query) is not None

    assert "token" in result
    assert result["msg"] == f"User {test_user_data['email']} registered and logged in"

    result = signup(test_user_data)

    assert "token" not in result
    assert (
        result["msg"]
        == f"An account with email: {test_user_data['email']} is already registered"
    )

    cleanup(db, test_user_data["email"])


def test_login(db, test_user_data):
    users_collection = db["users"]
    logged_in_collection = db["logged_in"]
    cleanup(db, test_user_data["email"])

    query = {"email": test_user_data["email"]}

    result = signup(test_user_data)

    _ = logout({"email": test_user_data["email"], "token": result["token"]})

    assert users_collection.find_one(query) is not None
    assert logged_in_collection.find_one(query) is None

    result = login({"email": test_user_data["email"], "password": "SomePassword123"})

    assert users_collection.find_one(query) is not None
    assert logged_in_collection.find_one(query) is not None

    assert "token" in result
    assert result["msg"] == f"{test_user_data['email']} is now logged in"

    cleanup(db, test_user_data["email"])


def test_logout(db, test_user_data):
    users_collection = db["users"]
    logged_in_collection = db["logged_in"]
    cleanup(db, test_user_data["email"])
    query = {"email": test_user_data["email"]}

    assert users_collection.find_one(query) is None
    assert logged_in_collection.find_one(query) is None

    result = signup(test_user_data)

    assert users_collection.find_one(query) is not None
    assert logged_in_collection.find_one(query) is not None

    assert "token" in result
    assert result["msg"] == f"User {test_user_data['email']} registered and logged in"

    logout_result = logout({"email": test_user_data["email"], "token": result["token"]})

    assert logout_result["msg"] == f"Successfully logged out {test_user_data['email']}"
    assert users_collection.find_one(query) is not None
    assert logged_in_collection.find_one(query) is None

    cleanup(db, test_user_data["email"])


def test_valid_email():
    assert valid_email("a1@b.co")
    assert valid_email("seng2021@gmail.com")

    assert not valid_email("@gmail.com")
    assert not valid_email("a@gmail")
    assert not valid_email("Someemailwithoutat")
    assert not valid_email("a @gmail.com")
    assert not valid_email("#$#@gmail.com")
    assert not valid_email("a@@@@@b.com")


def test_valid_password():
    assert valid_password("SomePassword123")
    assert valid_password("mYg0dabc")

    assert not valid_password("Ab12")
    assert not valid_password("somepassword123")
    assert not valid_password("SomePassword")
    assert not valid_password("mYg0d")


def test_valid_name():
    assert valid_name("Fredrick")
    assert valid_name("Fredrick-bob")
    assert valid_name("Gsp")

    assert not valid_name("")
