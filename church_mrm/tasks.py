import frappe
from frappe.utils import today, add_days, getdate


def update_membership_statuses():
    """Daily: Check all memberships and update status based on end_date."""
    memberships = frappe.get_all(
        "Membership",
        filters={"status": ["in", ["Current", "Grace"]], "is_override": 0},
        fields=["name", "end_date", "membership_type", "status"],
    )

    for m in memberships:
        if not m.end_date:
            continue
        if getdate(m.end_date) >= getdate(today()):
            continue

        grace_end = add_days(m.end_date, 30)
        if getdate(today()) > getdate(grace_end):
            frappe.db.set_value("Membership", m.name, "status", "Expired")
        elif m.status != "Grace":
            frappe.db.set_value("Membership", m.name, "status", "Grace")

    frappe.db.commit()


def send_pledge_reminders():
    """Daily: Send reminders for upcoming/overdue pledge payments."""
    upcoming = frappe.get_all(
        "Pledge Payment Schedule",
        filters={
            "status": "Pending",
            "scheduled_date": ["<=", add_days(today(), 5)],
        },
        fields=["name", "parent", "scheduled_date", "scheduled_amount"],
    )

    for payment in upcoming:
        try:
            pledge = frappe.get_doc("Pledge", payment.parent)
            member = frappe.get_doc("Church Member", pledge.church_member)
            if not member.email_address or member.do_not_email:
                continue

            frappe.sendmail(
                recipients=[member.email_address],
                subject=f"Pledge Payment Reminder - {pledge.name}",
                message=f"""Dear {member.first_name},

This is a reminder that your pledge payment of {payment.scheduled_amount} is due on {payment.scheduled_date}.

Thank you for your generous support.

PS Church""",
            )
            frappe.db.set_value(
                "Pledge Payment Schedule",
                payment.name,
                "reminder_count",
                (payment.get("reminder_count") or 0) + 1,
            )
        except Exception:
            frappe.log_error(f"Failed to send pledge reminder for {payment.name}")

    frappe.db.commit()
