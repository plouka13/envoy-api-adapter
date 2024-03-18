import pytest

from api_adapter.database import connect_to_db


def cleanup(db, email):
    users = db["users"]
    logged_in = db["logged_in"]

    users.delete_one({"email": email})
    logged_in.delete_one({"email": email})


@pytest.fixture
def db():
    return connect_to_db()
