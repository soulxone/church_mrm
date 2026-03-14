import frappe

no_cache = 1


def get_context(context):
    context.page_title = "Donate - PS Church"
    context.donation_types = frappe.get_all(
        "Donation Type",
        filters={"is_active": 1},
        fields=["name", "label"],
        order_by="sort_order asc",
    )
    return context


@frappe.whitelist(allow_guest=True)
def submit_donation(donor_name, email, donation_type, amount):
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    donation = frappe.new_doc("Donation")
    donation.donor_name = donor_name
    donation.donation_type = donation_type
    donation.amount = float(amount)
    donation.donation_date = frappe.utils.today()
    donation.payment_method = "Online"
    donation.company = company
    donation.source = "Website"
    donation.insert(ignore_permissions=True)
    return {"status": "success", "donation": donation.name}
