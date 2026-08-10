import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class TheatreShow(Document):

    def validate(self):
        self.validate_show_date()
        self.validate_total_seats()
        self.validate_ticket_price()

    def validate_show_date(self):
        if self.show_date and getdate(self.show_date) < getdate(today()):
            frappe.throw("Show Date cannot be in the past.")

    def validate_total_seats(self):
        if self.total_seats is not None and self.total_seats <= 0:
            frappe.throw("Total Seats must be greater than 0.")

    def validate_ticket_price(self):
        if self.ticket_price is not None and self.ticket_price < 0:
            frappe.throw("Ticket Price cannot be negative.")