frappe.ui.form.on("Church Member", {
    refresh: function(frm) {
        if (frm.doc.contact) {
            frm.add_custom_button(__("View Contact"), function() {
                frappe.set_route("Form", "Contact", frm.doc.contact);
            });
        }
        if (!frm.is_new()) {
            frm.add_custom_button(__("New Donation"), function() {
                frappe.new_doc("Donation", {
                    church_member: frm.doc.name,
                    donor_name: frm.doc.full_name
                });
            }, __("Create"));
            frm.add_custom_button(__("New Membership"), function() {
                frappe.new_doc("Membership", {
                    church_member: frm.doc.name,
                    member_name: frm.doc.full_name
                });
            }, __("Create"));
        }
    }
});
