frappe.query_reports["Event Attendance"] = {
    filters: [
        {
            fieldname: "event_type",
            label: __("Event Type"),
            fieldtype: "Select",
            options: "\nSunday Service\nBible Study\nConference\nWorkshop\nRetreat\nFellowship\nYouth Event\nOutreach\nFundraiser\nOther",
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
    ],
};
