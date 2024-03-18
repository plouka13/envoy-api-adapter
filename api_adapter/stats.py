"""
Calculate and create the stats of the users.
"""

import datetime

import xmltodict

from api_adapter.database import get_invoices
from api_adapter.helpers import get_time


def last_thirty_days_stats(token):
    """
    Earnings for the last thirty days is returned.
    """

    invoices, msg = get_invoices(token)

    list_stats = []

    for _ in range(0, 30):
        list_stats.append(0)

    # find today's date
    today_date = get_time()

    # find the date 30 days ago
    start_date = today_date - datetime.timedelta(30)

    curr_date = today_date

    i = 0

    while curr_date != start_date:

        for invoice in invoices["created"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if (
                invoice_datetime.month == curr_date.month
                and invoice_datetime.year == curr_date.year
                and invoice_datetime.day == curr_date.day
            ):

                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_stats[i] += float(monetary["cbc:PayableAmount"]["#text"])

        for invoice in invoices["received"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if (
                invoice_datetime.month == curr_date.month
                and invoice_datetime.year == curr_date.year
                and invoice_datetime.day == curr_date.day
            ):
                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_stats[i] += float(monetary["cbc:PayableAmount"]["#text"])

        # loop back each date
        curr_date -= datetime.timedelta(1)
        i += 1

    return {"msg": msg, "last_thirty_days": list_stats}


def curr_daily_stats(token):
    """
    Earnings for the month is returned.
    """

    invoices, msg = get_invoices(token)

    created_invoices = invoices["created"]

    daily_earns = 0

    # find today's date
    today_date = get_time()

    for invoice in created_invoices:
        time_of_invoice = invoice["timestamp"]

        # parse datetime
        invoice_datetime = datetime.datetime.strptime(
            time_of_invoice, "%d/%m/%Y, %H:%M:%S"
        )
        if (
            invoice_datetime.day == today_date.day
            and invoice_datetime.month == today_date.month
            and invoice_datetime.year == today_date.year
        ):
            inv_dict = xmltodict.parse(invoice["content"])
            monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
            daily_earns += float(monetary["cbc:PayableAmount"]["#text"])

    for invoice in invoices["received"]:
        time_of_invoice = invoice["timestamp"]

        # parse datetime
        invoice_datetime = datetime.datetime.strptime(
            time_of_invoice, "%d/%m/%Y, %H:%M:%S"
        )
        if (
            invoice_datetime.day == today_date.day
            and invoice_datetime.month == today_date.month
            and invoice_datetime.year == today_date.year
        ):
            inv_dict = xmltodict.parse(invoice["content"])
            monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
            daily_earns += float(monetary["cbc:PayableAmount"]["#text"])

    list_prev_days = []

    for _ in range(0, 5):
        list_prev_days.append(0)

    # find the date 5 months ago
    start_date = today_date - datetime.timedelta(5)

    curr_date = today_date

    i = 0

    while curr_date != start_date:

        for invoice in invoices["created"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if (
                invoice_datetime.day == curr_date.day
                and invoice_datetime.month == curr_date.month
                and invoice_datetime.year == curr_date.year
            ):
                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_prev_days[i] += float(monetary["cbc:PayableAmount"]["#text"])

        for invoice in invoices["received"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if (
                invoice_datetime.day == curr_date.day
                and invoice_datetime.month == curr_date.month
                and invoice_datetime.year == curr_date.year
            ):
                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_prev_days[i] += float(monetary["cbc:PayableAmount"]["#text"])

        # loop back each date
        curr_date -= datetime.timedelta(1)
        i += 1

    return {"msg": msg, "day_earns": daily_earns, "last_five_days": list_prev_days}


def curr_month_stats(token):
    """
    Earnings for the month is returned.
    """

    invoices, msg = get_invoices(token)

    created_invoices = invoices["created"]

    month_earns = 0

    # find today's date
    today_date = get_time()

    for invoice in created_invoices:
        time_of_invoice = invoice["timestamp"]

        # parse datetime
        invoice_datetime = datetime.datetime.strptime(
            time_of_invoice, "%d/%m/%Y, %H:%M:%S"
        )
        if (
            invoice_datetime.month == today_date.month
            and invoice_datetime.year == today_date.year
        ):
            inv_dict = xmltodict.parse(invoice["content"])
            monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
            month_earns += float(monetary["cbc:PayableAmount"]["#text"])

    for invoice in invoices["received"]:
        time_of_invoice = invoice["timestamp"]

        # parse datetime
        invoice_datetime = datetime.datetime.strptime(
            time_of_invoice, "%d/%m/%Y, %H:%M:%S"
        )
        if (
            invoice_datetime.month == today_date.month
            and invoice_datetime.year == today_date.year
        ):
            inv_dict = xmltodict.parse(invoice["content"])
            monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
            month_earns += float(monetary["cbc:PayableAmount"]["#text"])

    list_prev_months = []

    for _ in range(0, 5):
        list_prev_months.append(0)

    # find the date 5 months ago
    start_date = today_date - datetime.timedelta(5 * 30)

    curr_date = today_date

    i = 0

    while curr_date != start_date:

        for invoice in invoices["created"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if (
                invoice_datetime.month == curr_date.month
                and invoice_datetime.year == curr_date.year
            ):
                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_prev_months[i] += float(monetary["cbc:PayableAmount"]["#text"])

        for invoice in invoices["received"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if (
                invoice_datetime.month == curr_date.month
                and invoice_datetime.year == curr_date.year
            ):
                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_prev_months[i] += float(monetary["cbc:PayableAmount"]["#text"])

        # loop back each date
        curr_date -= datetime.timedelta(30)
        i += 1

    return {
        "msg": msg,
        "month_earns": month_earns,
        "last_five_months": list_prev_months,
    }


def curr_year_stats(token):
    """
    Earnings for the year is returned.
    """

    invoices, msg = get_invoices(token)

    created_invoices = invoices["created"]

    year_earns = 0

    # find today's date
    today_date = get_time()

    for invoice in created_invoices:
        time_of_invoice = invoice["timestamp"]

        # parse datetime
        invoice_datetime = datetime.datetime.strptime(
            time_of_invoice, "%d/%m/%Y, %H:%M:%S"
        )
        if invoice_datetime.year == today_date.year:
            inv_dict = xmltodict.parse(invoice["content"])
            monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
            year_earns += float(monetary["cbc:PayableAmount"]["#text"])

    for invoice in invoices["received"]:
        time_of_invoice = invoice["timestamp"]

        # parse datetime
        invoice_datetime = datetime.datetime.strptime(
            time_of_invoice, "%d/%m/%Y, %H:%M:%S"
        )
        if invoice_datetime.year == today_date.year:
            inv_dict = xmltodict.parse(invoice["content"])
            monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
            year_earns += float(monetary["cbc:PayableAmount"]["#text"])

    list_prev_years = []

    for _ in range(0, 5):
        list_prev_years.append(0)

    # find the date 5 years ago
    start_date = today_date - datetime.timedelta(5 * 365)

    curr_date = today_date

    i = 0

    while curr_date != start_date:

        for invoice in invoices["created"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if (
                invoice_datetime.month == curr_date.month
                and invoice_datetime.year == curr_date.year
            ):
                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_prev_years[i] += float(monetary["cbc:PayableAmount"]["#text"])

        for invoice in invoices["received"]:
            time_of_invoice = invoice["timestamp"]

            # parse datetime
            invoice_datetime = datetime.datetime.strptime(
                time_of_invoice, "%d/%m/%Y, %H:%M:%S"
            )

            if invoice_datetime.year == curr_date.year:
                inv_dict = xmltodict.parse(invoice["content"])
                monetary = inv_dict["Invoice"]["cac:LegalMonetaryTotal"]
                list_prev_years[i] += float(monetary["cbc:PayableAmount"]["#text"])

        # loop back each date
        curr_date -= datetime.timedelta(365)
        i += 1

    return {"msg": msg, "year_earns": year_earns, "last_five_years": list_prev_years}


def num_created_stats(token):
    """
    How many invoices created is returned.
    """

    invoices, msg = get_invoices(token)

    created_invoices = invoices["created"]

    return {"msg": msg, "num_created_inv": len(created_invoices)}


def num_received_stats(token):
    """

    How many invoices received is returned.
    """

    invoices, msg = get_invoices(token)

    received_invoices = invoices["received"]

    return {"msg": msg, "num_received_inv": len(received_invoices)}


def num_sent_stats(token):
    """
    How many invoices sent is returned.
    """

    invoices, msg = get_invoices(token)

    created_invoices = invoices["created"]

    num_sent = 0

    for invoice in created_invoices:
        if invoice["sent"]:
            num_sent += 1

    return {"msg": msg, "num_sent_inv": num_sent}
