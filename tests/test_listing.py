from api_adapter.database import login_user, register_user
from api_adapter.listing import list_invoices
from tests.test_database import cleanup

test_user_data = {
    "email": "test@email.com",
    "firstname": "test",
    "lastname": "email",
    "password": "somepassword",
}


def test_list_invoice(db):
    cleanup(db, test_user_data["email"])

    _ = register_user(test_user_data)
    token, _ = login_user(test_user_data["email"], test_user_data["password"])

    data = list_invoices(token)

    assert len(data["created_invoices"]) == 0
    assert len(data["received_invoices"]) == 0
    assert data["msg"] == "Successfully retreived invoices for test@email.com"

    users = db["users"]
    users_query = {"email": test_user_data["email"]}

    test_data = {"test": "data", "method": "created"}

    users.update_one(users_query, {"$push": {"invoices": test_data}})

    data = list_invoices(token)

    assert len(data["created_invoices"]) == 1
    assert len(data["received_invoices"]) == 0

    assert data["created_invoices"][0] == test_data
    assert data["msg"] == "Successfully retreived invoices for test@email.com"

    cleanup(db, test_user_data["email"])
