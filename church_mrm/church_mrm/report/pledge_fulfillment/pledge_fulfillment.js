frappe.query_reports["Pledge Fulfillment"] = {
    filters: [
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nPending\nIn Progress\nCompleted\nCancelled\nOverdue",
        },
    ],
};
