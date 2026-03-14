frappe.ui.form.on("Donation", {
    refresh: function(frm) {
        if (frm.doc.journal_entry) {
            frm.add_custom_button(__("View Journal Entry"), function() {
                frappe.set_route("Form", "Journal Entry", frm.doc.journal_entry);
            });
        }
    },
    church_member: function(frm) {
        if (frm.doc.church_member) {
            frappe.db.get_value("Church Member", frm.doc.church_member, "full_name", function(r) {
                if (r) frm.set_value("donor_name", r.full_name);
            });
        }
    }
});
