import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "name", "label": "Pledge", "fieldtype": "Link", "options": "Pledge", "width": 150},
        {"fieldname": "member_name", "label": "Member", "fieldtype": "Data", "width": 180},
        {"fieldname": "donation_type", "label": "Fund", "fieldtype": "Link", "options": "Donation Type", "width": 150},
        {"fieldname": "total_amount", "label": "Pledged", "fieldtype": "Currency", "width": 120},
        {"fieldname": "amount_paid", "label": "Paid", "fieldtype": "Currency", "width": 120},
        {"fieldname": "amount_outstanding", "label": "Outstanding", "fieldtype": "Currency", "width": 120},
        {"fieldname": "pct", "label": "% Fulfilled", "fieldtype": "Percent", "width": 100},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    conditions = {"docstatus": 1}
    if filters.get("status"):
        conditions["status"] = filters["status"]

    pledges = frappe.get_all(
        "Pledge",
        filters=conditions,
        fields=["name", "member_name", "donation_type", "total_amount", "amount_paid", "amount_outstanding", "status"],
        order_by="pledge_date desc",
    )
    for p in pledges:
        p["pct"] = flt(p["amount_paid"]) / flt(p["total_amount"]) * 100 if flt(p["total_amount"]) else 0
    return pledges
