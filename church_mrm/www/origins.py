import frappe

no_cache = 1


def get_context(context):
    context.page_title = "Origins of Ideas"
    context.no_breadcrumbs = True
    context.is_logged_in = frappe.session.user != "Guest"
    context.user_fullname = (
        frappe.utils.get_fullname(frappe.session.user)
        if context.is_logged_in
        else ""
    )
