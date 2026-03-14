frappe.query_reports["Giving Statement"] = {
    filters: [
        {
            fieldname: "church_member",
            label: __("Church Member"),
            fieldtype: "Link",
            options: "Church Member",
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
    ],
};
