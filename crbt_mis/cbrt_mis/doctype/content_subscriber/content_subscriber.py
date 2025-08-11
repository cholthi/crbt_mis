# Copyright (c) 2025, Philip Chol and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ContentSubscriber(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_submittable = True
