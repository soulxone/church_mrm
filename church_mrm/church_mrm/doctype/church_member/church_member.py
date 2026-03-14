import frappe
from frappe.model.document import Document


class ChurchMember(Document):
    def autoname(self):
        count = frappe.db.count("Church Member") + 1
        self.member_id = f"MBR-{count:04d}"
        self.name = self.member_id

    def validate(self):
        self.set_full_name()
        self.validate_dates()

    def set_full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        self.full_name = " ".join([p for p in parts if p])

    def validate_dates(self):
        if self.date_of_birth and self.baptism_date:
            if self.baptism_date < self.date_of_birth:
                frappe.throw("Baptism date cannot be before date of birth")

    def after_insert(self):
        self.create_or_link_contact()

    def create_or_link_contact(self):
        if self.contact:
            return
        contact = frappe.new_doc("Contact")
        contact.first_name = self.first_name
        contact.middle_name = self.middle_name
        contact.last_name = self.last_name
        contact.salutation = self.salutation
        contact.gender = self.gender
        if self.email_address:
            contact.append("email_ids", {
                "email_id": self.email_address,
                "is_primary": 1,
            })
        if self.phone:
            contact.append("phone_nos", {
                "phone": self.phone,
                "is_primary_phone": 1,
            })
        if self.mobile:
            contact.append("phone_nos", {
                "phone": self.mobile,
                "is_primary_mobile_no": 1,
            })
        contact.insert(ignore_permissions=True)
        self.db_set("contact", contact.name)
