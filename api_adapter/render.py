import os

import requests

from api_adapter.constants import RENDER_BASE_URL
from api_adapter.database import get_invoices
from api_adapter.render_json import conv_xml_format

# import zipfile


def save_invoice_locally(invoice_contents):
    directory = "invoices/"
    filename = "invoice.xml"
    file_path = os.path.join(directory, filename)
    if not os.path.isdir(directory):
        os.mkdir(directory)

    file = open(file_path, "w")
    file.write(invoice_contents)
    file.close()
    return file_path


def get_render(token: str, invoice_id: int) -> dict:
    unformatted_invoice_contents = get_invoice_contents(token, invoice_id)
    invoice_contents = conv_xml_format(unformatted_invoice_contents)
    upload_url = f"{RENDER_BASE_URL}upload"

    file_path = save_invoice_locally(invoice_contents)
    file = {
        "file": ("invoice.xml", open(file_path, "rb"), "text/xml"),
    }

    res = requests.post(upload_url, files=file)

    if res.ok:
        download_url = f"{RENDER_BASE_URL}download?file_id={res.json()['file_ids'][0]}&file_type=HTML"
        response = requests.get(download_url)

        return {"msg": "RENDERED", "content": response.text}

    return {"msg": "Error rendering"}


def get_invoice_contents(token, id):
    invoices, msg = get_invoices(token)

    for i in range(0, len(invoices["created"])):
        if str(invoices["created"][i]["invoice_id"]) == str(id):
            return invoices["created"][i]["content"]
    for i in range(0, len(invoices["received"])):
        if str(invoices["received"][i]["invoice_id"]) == str(id):
            return invoices["received"][i]["content"]
    return None
