import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "donation_type", "label": "Donation Type", "fieldtype": "Link", "options": "Donation Type", "width": 200},
        {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency", "width": 150},
        {"fieldname": "count", "label": "Count", "fieldtype": "Int", "width": 100},
        {"fieldname": "avg_amount", "label": "Average", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    conditions = "d.docstatus = 1"
    if filters.get("from_date"):
        conditions += f" AND d.donation_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND d.donation_date <= '{filters['to_date']}'"

    return frappe.db.sql(f"""
        SELECT
            d.donation_type,
            SUM(d.amount) as total_amount,
            COUNT(*) as count,
            AVG(d.amount) as avg_amount
        FROM `tabDonation` d
        WHERE {conditions}
        GROUP BY d.donation_type
        ORDER BY total_amount DESC
    """, as_dict=True)
