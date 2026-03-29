import frappe

no_cache = 1


def get_context(context):
    context.page_title = "Photo Gallery - PS Church"
    context.photos = frappe.get_all(
        "Church Gallery Photo",
        filters={"is_published": 1},
        fields=["name", "image", "caption", "category"],
        order_by="display_order asc, creation desc",
    )
    context.categories = frappe.get_all(
        "Gallery Category",
        fields=["category_name"],
        order_by="display_order asc",
    )
    return context
