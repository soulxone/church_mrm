import frappe
from frappe.model.document import Document


class ChurchRelationship(Document):
    def validate(self):
        if self.member_a == self.member_b:
            frappe.throw("A person cannot have a relationship with themselves")
