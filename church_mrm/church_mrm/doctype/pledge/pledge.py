import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_to_date


class Pledge(Document):
    def validate(self):
        self.calculate_installment_amount()
        self.generate_payment_schedule()
        self.calculate_outstanding()

    def calculate_installment_amount(self):
        if flt(self.total_amount) > 0 and self.installments:
            self.installment_amount = flt(self.total_amount) / self.installments

    def generate_payment_schedule(self):
        if self.payment_schedule or not self.start_date:
            return
        unit_map = {
            "Weekly": {"weeks": self.frequency_interval or 1},
            "Monthly": {"months": self.frequency_interval or 1},
            "Quarterly": {"months": (self.frequency_interval or 1) * 3},
            "Annually": {"years": self.frequency_interval or 1},
        }
        delta = unit_map.get(self.frequency_unit, {"months": 1})
        current_date = self.start_date
        for i in range(self.installments):
            self.append("payment_schedule", {
                "scheduled_date": current_date,
                "scheduled_amount": flt(self.installment_amount),
                "status": "Pending",
                "reminder_count": 0,
            })
            current_date = add_to_date(current_date, **delta)
        self.end_date = current_date

    def calculate_outstanding(self):
        self.amount_outstanding = flt(self.total_amount) - flt(self.amount_paid)
