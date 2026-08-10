import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class TheatreBooking(Document):

    def validate(self):
        self.validate_show_date()
        self.validate_duplicate_seat()
        self.validate_seat_number()

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

    def validate_seat_number(self):
        if not self.show or not self.seat_number:
            return

        total_seats = frappe.db.get_value(
            "Theatre Show",
            self.show,
            "total_seats"
        )

        try:
            seat_number = int(self.seat_number)
        except (ValueError, TypeError):
            frappe.throw("Seat Number must be a valid number.")

        if seat_number <= 0:
            frappe.throw("Seat Number must be greater than 0.")

        if seat_number > total_seats:
            frappe.throw(
                f"Seat Number cannot be greater than {total_seats}."
            )