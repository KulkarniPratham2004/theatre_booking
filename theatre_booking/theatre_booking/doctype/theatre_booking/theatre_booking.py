import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class TheatreBooking(Document):

    def validate(self):
        self.validate_show_date()
        self.validate_duplicate_seat()

    def validate_show_date(self):
        if not self.show:
            return

        show_date = frappe.db.get_value(
            "Theatre Show",
            self.show,
            "show_date"
        )

        if show_date and getdate(show_date) < getdate(today()):
            frappe.throw(
                "Cannot create a booking for a show whose date has passed."
            )

    def validate_duplicate_seat(self):
        if not self.show or not self.seat_number:
            return

        existing_booking = frappe.db.exists(
            "Theatre Booking",
            {
                "show": self.show,
                "seat_number": self.seat_number,
                "name": ["!=", self.name]
            }
        )

        if existing_booking:
            frappe.throw(
                f"Seat {self.seat_number} is already booked for this show."
            )