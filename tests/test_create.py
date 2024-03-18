import json
import xml.etree.ElementTree as ET

import pytest

from api_adapter.create import create_invoice

# not sure how to request to the server url.

OK = 200
INVALID_INPUT = 405


@pytest.fixture
def sample_invoice():
    with open("tests/test_data/test_invoice_input.json") as sample_invoice_file:
        return json.load(sample_invoice_file)


@pytest.fixture
def invalid_invoice():
    with open("tests/test_data/test_invalid_invoice_input.json") as sample_invoice_file:
        return json.load(sample_invoice_file)


def test_create_invoice_success(sample_invoice):
    """
    Testing to have an invoice created, validated and stored

    Should create invoice with no error.
    """

    result = create_invoice(sample_invoice)

    assert result.status_code == OK
    expected_data = ET.parse("tests/test_data/test_valid_response.xml").getroot()
    response_data = ET.fromstring(result.text)
    assert expected_data.items() == response_data.items()


def test_create_invoice_error_invalid_input(invalid_invoice):
    """
    Testing to have an invoice created but it is invalid input

    Should return error.
    """
    # invalid input
    result = create_invoice(invalid_invoice)
    assert result.status_code == OK
    with pytest.raises(Exception):
        _ = ET.fromstring(result.text)

    result = create_invoice({"test": "invalid"})
    assert result.status_code == OK
    with pytest.raises(Exception):
        _ = ET.fromstring(result.text)
