import frappe

no_cache = 1


def get_context(context):
    context.page_title = "Membership Signup - PS Church"
    return context


@frappe.whitelist(allow_guest=True)
def submit_signup(first_name, last_name, email, phone=None):
    member = frappe.new_doc("Church Member")
    member.first_name = first_name
    member.last_name = last_name
    member.email_address = email
    member.phone = phone
    member.membership_status = "New"
    member.member_since = frappe.utils.today()
    member.insert(ignore_permissions=True)
    return {"status": "success", "member": member.name}
