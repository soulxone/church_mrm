import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "event_name", "label": "Event", "fieldtype": "Data", "width": 250},
        {"fieldname": "event_type", "label": "Type", "fieldtype": "Data", "width": 150},
        {"fieldname": "start_date", "label": "Date", "fieldtype": "Datetime", "width": 180},
        {"fieldname": "registered", "label": "Registered", "fieldtype": "Int", "width": 100},
        {"fieldname": "attended", "label": "Attended", "fieldtype": "Int", "width": 100},
        {"fieldname": "no_show", "label": "No-Show", "fieldtype": "Int", "width": 100},
    ]


def get_data(filters):
    conditions = "1=1"
    if filters.get("event_type"):
        conditions += f" AND e.event_type = '{filters['event_type']}'"
    if filters.get("from_date"):
        conditions += f" AND e.start_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND e.start_date <= '{filters['to_date']}'"

    return frappe.db.sql(f"""
        SELECT
            e.name,
            e.event_name,
            e.event_type,
            e.start_date,
            (SELECT COUNT(*) FROM `tabEvent Participant` p WHERE p.parent = e.name AND p.status = 'Registered') as registered,
            (SELECT COUNT(*) FROM `tabEvent Participant` p WHERE p.parent = e.name AND p.status = 'Attended') as attended,
            (SELECT COUNT(*) FROM `tabEvent Participant` p WHERE p.parent = e.name AND p.status = 'No-Show') as no_show
        FROM `tabChurch Event` e
        WHERE {conditions}
        ORDER BY e.start_date DESC
    """, as_dict=True)
