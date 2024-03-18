"""
Functionality for the send endpoint
- Takes a UBL file and sends it toanother user
- Generates a status report
"""

import os

import requests


def send_invoice(input):
    data1 = {
        "token": input["token"],
        "invoiceTitle": input["invoiceTitle"],
        "mailContent": input["mailContent"],
        "recipientEmail": input["recipientEmail"],
    }
    f = open("xml_file.xml", "w")
    f.write(input["file"])
    f.close()

    file = open("xml_file.xml")
    data2 = {"file": file}
    url = "https://honeycomb-prod.herokuapp.com/send"
    post_val = requests.post(url, data=data1, files=data2)
    file.close()
    os.remove("xml_file.xml")
    return {"response": post_val.text, "response_code": post_val.status_code}
