import frappe

no_cache = 1


def get_context(context):
    context.page_title = "Church Events - PS Church"
    context.events = frappe.get_all(
        "Church Event",
        filters={"is_public": 1, "status": ["in", ["Planned", "Active"]]},
        fields=["event_name", "event_type", "start_date", "end_date", "venue", "summary", "image", "is_online", "online_meeting_url"],
        order_by="start_date asc",
    )
    return context
