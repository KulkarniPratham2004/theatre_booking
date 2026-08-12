
app_name = "theatre_booking"
app_title = "Theatre Booking"
app_publisher = "Prathamesh Kulkarni"
app_description = "Theatre Ticket Booking System"
app_email = "ikulkarniprathmesh@gmail.com"
app_license = "mit"


# ---------------------------------------------------------
# Scheduled Tasks
# ---------------------------------------------------------

scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "theatre_booking.api.update_show_statuses"
        ]
    }
}
