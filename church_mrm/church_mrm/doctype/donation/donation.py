import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Donation(Document):
    def validate(self):
        if flt(self.amount) <= 0:
            frappe.throw("Donation amount must be greater than zero")
        if self.church_member and not self.donor_name:
            self.donor_name = frappe.db.get_value(
                "Church Member", self.church_member, "full_name"
            )

    def on_submit(self):
        self.create_journal_entry()
        if self.pledge:
            self.update_pledge()

    def on_cancel(self):
        if self.journal_entry:
            je = frappe.get_doc("Journal Entry", self.journal_entry)
            if je.docstatus == 1:
                je.cancel()
            self.db_set("journal_entry", "")

    def create_journal_entry(self):
        if self.journal_entry:
            return
        donation_type = frappe.get_doc("Donation Type", self.donation_type)
        je = frappe.new_doc("Journal Entry")
        je.posting_date = self.donation_date
        je.company = self.company
        je.voucher_type = "Journal Entry"
        je.user_remark = f"Donation {self.name} - {self.donor_name or 'Anonymous'}"
        je.append("accounts", {
            "account": donation_type.debit_account,
            "debit_in_account_currency": flt(self.amount),
        })
        je.append("accounts", {
            "account": donation_type.income_account,
            "credit_in_account_currency": flt(self.amount),
        })
        je.insert(ignore_permissions=True)
        je.submit()
        self.db_set("journal_entry", je.name)

    def update_pledge(self):
        pledge = frappe.get_doc("Pledge", self.pledge)
        for row in pledge.payment_schedule:
            if row.status == "Pending":
                row.status = "Paid"
                row.actual_amount = flt(self.amount)
                row.donation = self.name
                row.paid_date = self.donation_date
                row.save()
                break
        paid = sum(flt(r.actual_amount) for r in pledge.payment_schedule if r.status == "Paid")
        pledge.db_set("amount_paid", paid)
        pledge.db_set("amount_outstanding", flt(pledge.total_amount) - paid)
        if paid >= flt(pledge.total_amount):
            pledge.db_set("status", "Completed")
        elif paid > 0:
            pledge.db_set("status", "In Progress")
