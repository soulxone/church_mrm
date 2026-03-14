import frappe


def validate_contact(doc, method):
    """Sync church member data when Contact is updated."""
    if doc.get("church_member"):
        member = frappe.get_doc("Church Member", doc.church_member)
        if member.email_address != doc.email_id:
            member.db_set("email_address", doc.email_id)
