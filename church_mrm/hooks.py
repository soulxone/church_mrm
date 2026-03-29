app_name = "church_mrm"
app_title = "Church MRM"
app_publisher = "PS Church"
app_description = "Church MRM - Nonprofit CRM for Frappe/ERPNext inspired by CiviCRM"
app_email = "soulxone@gmail.com"
app_license = "AGPLv3"
required_apps = ["frappe", "erpnext"]

# App Icon (shown in Desk sidebar and module page)
app_icon = "/assets/church_mrm/images/church_mrm.svg"
app_color = "#6C5CE7"
app_icon_color = "#FFFFFF"

after_install = "church_mrm.install.after_install"

# Include CSS and JS in all pages
app_include_css = [
    "/assets/church_mrm/css/church_mrm.css",
    "/assets/church_mrm/css/photo_editor.css"
]
app_include_js = [
    "/assets/church_mrm/js/church_mrm.js",
    "/assets/church_mrm/js/photo_editor.js"
]

# Include JS on website portal pages
web_include_js = "/assets/church_mrm/js/website.js"

# Extend existing ERPNext DocTypes
doctype_js = {
    "Contact": "public/js/contact.js"
}

doc_events = {
    "Contact": {
        "validate": "church_mrm.overrides.contact.validate_contact",
    }
}

# Fixtures - Custom Fields added to existing DocTypes
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Church MRM"]]
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "Church MRM"]]
    },
    {
        "dt": "Number Card",
        "filters": [["module", "=", "Church MRM"]]
    },
    {
        "dt": "Dashboard Chart",
        "filters": [["module", "=", "Church MRM"]]
    },
    {
        "dt": "Onboarding Step",
        "filters": [["module", "=", "Church MRM"]]
    },
    {
        "dt": "Module Onboarding",
        "filters": [["module", "=", "Church MRM"]]
    },
    {
        "dt": "Workspace",
        "filters": [["module", "=", "Church MRM"]]
    }
]

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "church_mrm.tasks.update_membership_statuses",
        "church_mrm.tasks.send_pledge_reminders"
    ],
}

# Website routes
website_route_rules = [
    {"from_route": "/donate", "to_route": "donate"},
    {"from_route": "/church-events", "to_route": "church_events"},
    {"from_route": "/membership-signup", "to_route": "membership_signup"},
    {"from_route": "/expense-scanner", "to_route": "expense_scanner"},
    {"from_route": "/origins", "to_route": "origins"},
    {"from_route": "/events/detail", "to_route": "events/detail"},
    {"from_route": "/gallery", "to_route": "gallery"},
]

# Website context for portal
website_context = {
    "favicon": "/assets/church_mrm/images/church_mrm.svg",
    "splash_image": "/assets/church_mrm/images/og-banner.png",
}
