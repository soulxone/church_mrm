import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "donation_date", "label": "Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "name", "label": "Receipt #", "fieldtype": "Link", "options": "Donation", "width": 150},
        {"fieldname": "donation_type", "label": "Type", "fieldtype": "Link", "options": "Donation Type", "width": 150},
        {"fieldname": "payment_method", "label": "Payment Method", "fieldtype": "Data", "width": 120},
        {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "width": 120},
        {"fieldname": "is_tax_deductible", "label": "Tax Deductible", "fieldtype": "Check", "width": 100},
    ]


def get_data(filters):
    conditions = {"docstatus": 1}
    if filters.get("church_member"):
        conditions["church_member"] = filters["church_member"]
    if filters.get("from_date"):
        conditions["donation_date"] = [">=", filters["from_date"]]
    if filters.get("to_date"):
        conditions["donation_date"] = ["<=", filters["to_date"]]
    if filters.get("from_date") and filters.get("to_date"):
        conditions["donation_date"] = ["between", [filters["from_date"], filters["to_date"]]]

    return frappe.get_all(
        "Donation",
        filters=conditions,
        fields=["donation_date", "name", "donation_type", "payment_method", "amount", "is_tax_deductible"],
        order_by="donation_date asc",
    )
