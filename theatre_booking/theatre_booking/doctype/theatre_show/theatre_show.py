# Copyright (c) 2026, Prathamesh Kulkarni and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class TheatreShow(Document):

    def validate(self):
        self.validate_show_date()

    def validate_show_date(self):
        if self.show_date and getdate(self.show_date) < getdate(today()):
            frappe.throw("Show Date cannot be in the past.") 