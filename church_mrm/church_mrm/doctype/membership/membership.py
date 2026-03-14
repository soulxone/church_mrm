import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, getdate, today


class Membership(Document):
    def validate(self):
        self.calculate_end_date()

    def after_insert(self):
        self.update_member_status()

    def on_update(self):
        self.update_member_status()

    def calculate_end_date(self):
        if not self.end_date and self.membership_type and self.start_date:
            mt = frappe.get_doc("Membership Type", self.membership_type)
            unit_map = {"Day": "days", "Month": "months", "Year": "years"}
            unit = unit_map.get(mt.duration_unit, "years")
            self.end_date = add_to_date(
                self.start_date, **{unit: mt.duration_interval}
            )

    def update_member_status(self):
        if self.church_member:
            frappe.db.set_value(
                "Church Member",
                self.church_member,
                "membership_status",
                self.status,
            )
