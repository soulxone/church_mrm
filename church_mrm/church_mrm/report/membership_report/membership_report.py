import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "membership_type", "label": "Membership Type", "fieldtype": "Link", "options": "Membership Type", "width": 200},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 120},
        {"fieldname": "count", "label": "Count", "fieldtype": "Int", "width": 100},
    ]


def get_data(filters):
    conditions = "1=1"
    if filters.get("membership_type"):
        conditions += f" AND m.membership_type = '{filters['membership_type']}'"
    if filters.get("status"):
        conditions += f" AND m.status = '{filters['status']}'"

    return frappe.db.sql(f"""
        SELECT
            m.membership_type,
            m.status,
            COUNT(*) as count
        FROM `tabMembership` m
        WHERE {conditions}
        GROUP BY m.membership_type, m.status
        ORDER BY m.membership_type, m.status
    """, as_dict=True)
