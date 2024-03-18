import xmltodict

from api_adapter.database import get_invoices, login_user, register_user, store_invoice
from api_adapter.render import get_render
from api_adapter.render_json import conv_xml_format


def test_correct_outputs():
    resp = conv_xml_format(open("tests/test_data/sample_response.xml").read())
    resp = xmltodict.parse(resp)

    xml_string = open("tests/test_data/sample_response.xml").read()
    input_xml = xmltodict.parse(xml_string)

    assert (
        resp["Invoice"]["cbc:ID"] == input_xml["Invoice"]["cbc:ID"]
        and resp["Invoice"]["cbc:ID"] == "EBWASP1234"
    )
    assert (
        resp["Invoice"]["cac:InvoiceLine"]["cac:Item"]["cac:ClassifiedTaxCategory"][
            "cac:TaxScheme"
        ]["cbc:ID"]["#text"]
        == input_xml["Invoice"]["cac:InvoiceLine"]["cac:Item"][
            "cac:ClassifiedTaxCategory"
        ]["cac:TaxScheme"]["cbc:ID"]
    )
    assert resp["Invoice"]["cbc:DocumentCurrencyCode"]["#text"] == "NZD"
    assert (
        resp["Invoice"]["cac:InvoiceLine"]["cac:Item"]["cbc:Name"]
        == input_xml["Invoice"]["cac:InvoiceLine"]["cac:Item"]["cbc:Name"]
    )
    assert resp["Invoice"]["cac:InvoiceLine"]["cac:Item"]["cbc:Name"] == "Notebooks"
    assert resp["Invoice"]["cbc:IssueDate"] == input_xml["Invoice"]["cbc:IssueDate"]
    assert resp["Invoice"]["cbc:IssueDate"] == "2022-01-19"
    assert float(
        resp["Invoice"]["cac:LegalMonetaryTotal"]["cbc:PayableAmount"]["#text"]
    ) == float(
        input_xml["Invoice"]["cac:LegalMonetaryTotal"]["cbc:PayableAmount"]["#text"]
    )
    assert (
        resp["Invoice"]["cac:LegalMonetaryTotal"]["cbc:PayableAmount"]["#text"]
        == "510.00"
    )
    assert float(
        resp["Invoice"]["cac:InvoiceLine"]["cbc:InvoicedQuantity"]["#text"]
    ) == float(input_xml["Invoice"]["cac:InvoiceLine"]["cbc:InvoicedQuantity"])
    assert (
        resp["Invoice"]["cac:InvoiceLine"]["cbc:InvoicedQuantity"]["#text"] == "124.0"
    )
    assert float(
        resp["Invoice"]["cac:InvoiceLine"]["cbc:LineExtensionAmount"]["#text"]
    ) == float(
        input_xml["Invoice"]["cac:InvoiceLine"]["cbc:LineExtensionAmount"]["#text"]
    )
    assert (
        resp["Invoice"]["cac:InvoiceLine"]["cbc:LineExtensionAmount"]["#text"]
        == "500.00"
    )
    assert (
        resp["Invoice"]["cac:PaymentTerms"]["cbc:Note"]
        == input_xml["Invoice"]["cac:PaymentTerms"]["cbc:Note"]
    )
    assert resp["Invoice"]["cac:PaymentTerms"]["cbc:Note"] == "Paid"
    assert float(resp["Invoice"]["cac:TaxTotal"]["cbc:TaxAmount"]["#text"]) == float(
        input_xml["Invoice"]["cac:TaxTotal"]["cbc:TaxAmount"]["#text"]
    )
    assert resp["Invoice"]["cac:TaxTotal"]["cbc:TaxAmount"]["#text"] == "10.00"
    assert float(
        resp["Invoice"]["cac:TaxTotal"]["cac:TaxSubtotal"]["cbc:TaxableAmount"]["#text"]
    ) == float(
        input_xml["Invoice"]["cac:TaxTotal"]["cac:TaxSubtotal"]["cbc:TaxableAmount"][
            "#text"
        ]
    )
    assert float(
        resp["Invoice"]["cac:LegalMonetaryTotal"]["cbc:TaxExclusiveAmount"]["#text"]
    ) == float(
        input_xml["Invoice"]["cac:LegalMonetaryTotal"]["cbc:TaxExclusiveAmount"][
            "#text"
        ]
    )
    assert float(
        resp["Invoice"]["cac:LegalMonetaryTotal"]["cbc:TaxInclusiveAmount"]["#text"]
    ) == float(
        input_xml["Invoice"]["cac:LegalMonetaryTotal"]["cbc:TaxInclusiveAmount"][
            "#text"
        ]
    )
    assert (
        resp["Invoice"]["cac:TaxTotal"]["cac:TaxSubtotal"]["cac:TaxCategory"][
            "cac:TaxScheme"
        ]["cbc:ID"]["#text"]
        == input_xml["Invoice"]["cac:TaxTotal"]["cac:TaxSubtotal"]["cac:TaxCategory"][
            "cac:TaxScheme"
        ]["cbc:ID"]
    )
    assert (
        resp["Invoice"]["cac:TaxTotal"]["cac:TaxSubtotal"]["cac:TaxCategory"][
            "cac:TaxScheme"
        ]["cbc:ID"]["#text"]
        == "GSX"
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PartyLegalEntity"
        ]["cbc:RegistrationName"]
        == input_xml["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PartyLegalEntity"
        ]["cbc:RegistrationName"]
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PartyLegalEntity"
        ]["cbc:RegistrationName"]
        == "My Software Service Pty Ltd"
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:StreetName"]
        == input_xml["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:StreetName"]
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:StreetName"]
        == "123 Clark St"
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:CityName"]
        == input_xml["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:CityName"]
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:CityName"]
        == "Sydney"
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:PostalZone"]
        == input_xml["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:PostalZone"]
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:PostalZone"]
        == "2000"
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cac:Country"]["cbc:IdentificationCode"]["#text"]
        == input_xml["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cac:Country"]["cbc:IdentificationCode"]
    )
    assert (
        resp["Invoice"]["cac:AccountingSupplierParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cac:Country"]["cbc:IdentificationCode"]["#text"]
        == "NZ"
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PartyLegalEntity"
        ]["cbc:RegistrationName"]
        == input_xml["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PartyLegalEntity"
        ]["cbc:RegistrationName"]
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PartyLegalEntity"
        ]["cbc:RegistrationName"]
        == "My Registration Name"
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:StreetName"]
        == input_xml["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:StreetName"]
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:StreetName"]
        == "Side A"
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:CityName"]
        == input_xml["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:CityName"]
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:CityName"]
        == "Kensington"
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:PostalZone"]
        == input_xml["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:PostalZone"]
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cbc:PostalZone"]
        == "2019"
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cac:Country"]["cbc:IdentificationCode"]["#text"]
        == input_xml["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cac:Country"]["cbc:IdentificationCode"]
    )
    assert (
        resp["Invoice"]["cac:AccountingCustomerParty"]["cac:Party"][
            "cac:PostalAddress"
        ]["cac:Country"]["cbc:IdentificationCode"]["#text"]
        == "NZ"
    )


def test_with_database():
    register_user({"email": "emily@gmail.com", "password": "myDB1234"})
    token, resp = login_user("emily@gmail.com", "myDB1234")
    store_invoice(token, open("tests/test_data/sample_response.xml").read(), "created")
    store_invoice(token, open("tests/test_data/sample_response.xml").read(), "received")

    invoices, resp = get_invoices(token)

    created_id = invoices["created"][0]["invoice_id"]
    received_id = invoices["received"][0]["invoice_id"]

    created_response = get_render(token, created_id)
    assert created_response["msg"] == "RENDERED"

    received_response = get_render(token, received_id)
    assert received_response["msg"] == "RENDERED"
