import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class TheatreShow(Document):

    def validate(self):
        self.validate_show_date()
        self.validate_total_seats()

    def validate_show_date(self):
        if self.show_date and getdate(self.show_date) < getdate(today()):
            frappe.throw("Show Date cannot be in the past.")

    def validate_total_seats(self):
        if self.total_seats is not None and self.total_seats <= 0:
            frappe.throw("Total Seats must be greater than 0.")