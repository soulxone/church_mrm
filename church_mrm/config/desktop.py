from frappe import _


def get_data():
    return [
        {
            "module_name": "Church MRM",
            "color": "#6C5CE7",
            "icon": "/assets/church_mrm/images/church_mrm.svg",
            "type": "module",
            "label": _("Church MRM"),
            "description": _("Church membership, donations, events, and ministry management."),
            "onboard_present": 1,
        }
    ]
