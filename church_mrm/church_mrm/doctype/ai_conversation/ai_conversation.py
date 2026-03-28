import frappe
from frappe.model.document import Document
import uuid


class AIConversation(Document):
    def before_insert(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.title:
            self.title = "New Conversation"

    def validate(self):
        if self.messages:
            last = self.messages[-1]
            self.last_message_at = last.timestamp or frappe.utils.now()
