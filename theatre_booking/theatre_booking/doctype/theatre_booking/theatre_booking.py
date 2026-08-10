import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, get_time, now_datetime
from datetime import datetime


class TheatreBooking(Document):

    def validate(self):
        self.validate_show_date()
        self.validate_duplicate_seat()
        self.validate_seat_number()
        self.validate_booking_date()
        self.validate_status()
        self.validate_cancellation_time()
        self.set_booking_amount()

    # ---------------------------------------------------------
    # Validation 1:
    # Cannot book a show whose date has already passed
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Validation 2:
    # Prevent duplicate booking of the same seat
    # ---------------------------------------------------------
    def validate_duplicate_seat(self):

        if not self.show or not self.seat_number:
            return

        # Cancelled bookings do not occupy seats
        if self.status == "Cancelled":
            return

        existing_booking = frappe.db.exists(
            "Theatre Booking",
            {
                "show": self.show,
                "seat_number": self.seat_number,
                "status": "Booked",
                "name": ["!=", self.name]
            }
        )

        if existing_booking:
            frappe.throw(
                f"Seat {self.seat_number} is already booked for this show."
            )

    # ---------------------------------------------------------
    # Validation 3:
    # Seat number must be between 1 and Total Seats
    # ---------------------------------------------------------
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
            frappe.throw(
                "Seat Number must be a valid number."
            )

        if seat_number <= 0:
            frappe.throw(
                "Seat Number must be greater than 0."
            )

        if seat_number > total_seats:
            frappe.throw(
                f"Seat Number cannot be greater than {total_seats}."
            )

    # ---------------------------------------------------------
    # Validation 4:
    # Booking Date cannot be in the past
    # ---------------------------------------------------------
    def validate_booking_date(self):

        if self.booking_date:

            if getdate(self.booking_date) < getdate(today()):
                frappe.throw(
                    "Booking Date cannot be in the past."
                )

    # ---------------------------------------------------------
    # Validation 5:
    # Status must be Booked or Cancelled
    # ---------------------------------------------------------
    def validate_status(self):

        if self.status not in ["Booked", "Cancelled"]:
            frappe.throw(
                "Invalid booking status."
            )

    # ---------------------------------------------------------
    # Validation 6:
    # Cancellation is not allowed after show starts
    # ---------------------------------------------------------
    def validate_cancellation_time(self):

        # Only check when cancelling
        if self.status != "Cancelled":
            return

        if not self.show:
            return

        show_data = frappe.db.get_value(
            "Theatre Show",
            self.show,
            ["show_date", "show_time"],
            as_dict=True
        )

        if not show_data:
            frappe.throw(
                "Theatre Show could not be found."
            )

        if not show_data.show_date or not show_data.show_time:
            frappe.throw(
                "Show Date and Show Time are required."
            )

        show_datetime = datetime.combine(
            getdate(show_data.show_date),
            get_time(show_data.show_time)
        )

        current_datetime = now_datetime()

        if current_datetime >= show_datetime:
            frappe.throw(
                "Booking cannot be cancelled because the show has already started."
            )

    # ---------------------------------------------------------
    # Validation 7:
    # Automatically get Ticket Price from Theatre Show
    # ---------------------------------------------------------
    def set_booking_amount(self):

        if not self.show:
            return

        ticket_price = frappe.db.get_value(
            "Theatre Show",
            self.show,
            "ticket_price"
        )

        self.amount = ticket_price or 0