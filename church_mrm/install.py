import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    create_contact_custom_fields()
    create_default_donation_types()
    create_default_membership_types()
    create_default_relationship_types()
    create_workspace_sidebar()
    create_desktop_icon()


def create_contact_custom_fields():
    custom_fields = {
        "Contact": [
            dict(
                fieldname="church_member",
                fieldtype="Link",
                label="Church Member",
                options="Church Member",
                insert_after="user",
                module="Church MRM",
            ),
            dict(
                fieldname="is_church_member",
                fieldtype="Check",
                label="Is Church Member",
                insert_after="church_member",
                module="Church MRM",
            ),
        ]
    }
    create_custom_fields(custom_fields, update=True)


def create_default_donation_types():
    types = [
        {"donation_type_name": "Tithe", "label": "Tithe", "is_tax_deductible": 1},
        {"donation_type_name": "General Offering", "label": "General Offering", "is_tax_deductible": 1},
        {"donation_type_name": "Building Fund", "label": "Building Fund", "is_tax_deductible": 1},
        {"donation_type_name": "Missions", "label": "Missions", "is_tax_deductible": 1},
        {"donation_type_name": "Benevolence Fund", "label": "Benevolence Fund", "is_tax_deductible": 1},
        {"donation_type_name": "Special Offering", "label": "Special Offering", "is_tax_deductible": 1},
        {"donation_type_name": "Youth Ministry", "label": "Youth Ministry", "is_tax_deductible": 1},
        {"donation_type_name": "Music Ministry", "label": "Music Ministry", "is_tax_deductible": 1},
    ]
    for t in types:
        if not frappe.db.exists("Donation Type", t["donation_type_name"]):
            doc = frappe.new_doc("Donation Type")
            doc.update(t)
            doc.is_active = 1
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True)
    frappe.db.commit()


def create_default_membership_types():
    types = [
        {"type_name": "Regular Member", "title": "Regular Member", "duration_interval": 1, "duration_unit": "Year", "period_type": "Rolling"},
        {"type_name": "Youth Member", "title": "Youth Member", "duration_interval": 1, "duration_unit": "Year", "period_type": "Rolling"},
        {"type_name": "Senior Member", "title": "Senior Member", "duration_interval": 1, "duration_unit": "Year", "period_type": "Rolling"},
        {"type_name": "Associate Member", "title": "Associate Member", "duration_interval": 1, "duration_unit": "Year", "period_type": "Rolling"},
    ]
    for t in types:
        if not frappe.db.exists("Membership Type", t["type_name"]):
            doc = frappe.new_doc("Membership Type")
            doc.update(t)
            doc.is_active = 1
            doc.insert(ignore_permissions=True)
    frappe.db.commit()


def create_default_relationship_types():
    types = [
        {"relationship_type": "Spouse", "label_a_to_b": "is spouse of", "label_b_to_a": "is spouse of"},
        {"relationship_type": "Parent-Child", "label_a_to_b": "is parent of", "label_b_to_a": "is child of"},
        {"relationship_type": "Sibling", "label_a_to_b": "is sibling of", "label_b_to_a": "is sibling of"},
        {"relationship_type": "Head of Household", "label_a_to_b": "is head of household for", "label_b_to_a": "is member of household of"},
    ]
    for t in types:
        if not frappe.db.exists("Church Relationship Type", t["relationship_type"]):
            doc = frappe.new_doc("Church Relationship Type")
            doc.update(t)
            doc.is_active = 1
            doc.insert(ignore_permissions=True)
    frappe.db.commit()


def create_workspace_sidebar():
    """Create the Workspace Sidebar record so Church MRM appears in the desk sidebar."""
    if not frappe.db.exists("Workspace Sidebar", "Church MRM"):
        doc = frappe.new_doc("Workspace Sidebar")
        doc.name = "Church MRM"
        doc.title = "Church MRM"
        doc.header_icon = "heart"
        doc.module = "Church MRM"
        doc.standard = 0
        doc.append("items", {
            "label": "Home",
            "link_type": "Workspace",
            "type": "Link",
            "link_to": "Church MRM",
            "child": 0,
            "collapsible": 1,
            "indent": 0,
            "idx": 1,
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_desktop_icon():
    """Create the Desktop Icon so Church MRM appears on the desk home page."""
    if not frappe.db.exists("Desktop Icon", "Church MRM"):
        doc = frappe.new_doc("Desktop Icon")
        doc.label = "Church MRM"
        doc.icon_type = "Link"
        doc.link_type = "Workspace Sidebar"
        doc.link_to = "Church MRM"
        doc.icon = "heart"
        doc.app = "church_mrm"
        doc.bg_color = "blue"
        doc.hidden = 0
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
