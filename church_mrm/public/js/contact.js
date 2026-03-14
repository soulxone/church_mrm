frappe.ui.form.on("Contact", {
    refresh: function(frm) {
        if (frm.doc.church_member) {
            frm.add_custom_button(__("View Church Member"), function() {
                frappe.set_route("Form", "Church Member", frm.doc.church_member);
            }, __("Church MRM"));
        }
    }
});
