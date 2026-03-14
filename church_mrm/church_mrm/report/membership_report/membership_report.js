frappe.query_reports["Membership Report"] = {
    filters: [
        {
            fieldname: "membership_type",
            label: __("Membership Type"),
            fieldtype: "Link",
            options: "Membership Type",
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nNew\nCurrent\nGrace\nExpired\nCancelled\nDeceased\nPending",
        },
    ],
};
