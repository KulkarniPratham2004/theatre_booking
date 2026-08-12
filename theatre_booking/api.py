
import frappe


@frappe.whitelist(allow_guest=True)
def theatre_ai_summary():

    shows = frappe.get_all(
        "Theatre Show",
        ignore_permissions=True,
        fields=[
            "name",
            "movie_name",
            "show_date",
            "show_time",
            "screen",
            "total_seats",
            "ticket_price",
            "custom_status",
            "custom_end_time"
        ]
    )

    bookings = frappe.get_all(
        "Theatre Booking",
        fields=[
            "name",
            "show",
            "seat_number",
            "status",
            "amount"
        ]
    )

    # -----------------------------
    # SHOW STATISTICS
    # -----------------------------

    running = sum(
        1 for show in shows
        if show.custom_status == "Running"
    )

    upcoming = sum(
        1 for show in shows
        if show.custom_status == "Upcoming"
    )

    completed = sum(
        1 for show in shows
        if show.custom_status == "Completed"
    )

    cancelled = sum(
        1 for show in shows
        if show.custom_status == "Cancelled"
    )

    # -----------------------------
    # BOOKING STATISTICS
    # -----------------------------

    booked = sum(
        1 for booking in bookings
        if booking.status == "Booked"
    )

    cancelled_bookings = sum(
        1 for booking in bookings
        if booking.status == "Cancelled"
    )

    total_bookings = len(bookings)

    # -----------------------------
    # OCCUPANCY
    # -----------------------------

    total_seats = sum(
        (show.total_seats or 0)
        for show in shows
    )

    booked_seats_by_show = {}

    for booking in bookings:

        if booking.status != "Booked":
            continue

        if booking.show:
            booked_seats_by_show[booking.show] = (
                booked_seats_by_show.get(booking.show, 0) + 1
            )

    occupancy = 0

    if total_seats:
        occupancy = round(
            (booked / total_seats) * 100,
            2
        )

    # -----------------------------
    # SHOW-WISE OCCUPANCY
    # -----------------------------

    show_occupancy = []

    for show in shows:

        booked_for_show = booked_seats_by_show.get(
            show.name,
            0
        )

        seats = show.total_seats or 0

        occupancy_percentage = 0

        if seats:
            occupancy_percentage = round(
                (booked_for_show / seats) * 100,
                2
            )

        show_occupancy.append({
            "show": show.name,
            "movie_name": show.movie_name,
            "total_seats": seats,
            "booked_seats": booked_for_show,
            "available_seats": max(
                seats - booked_for_show,
                0
            ),
            "occupancy": occupancy_percentage
        })

    # -----------------------------
    # REVENUE
    # -----------------------------

    revenue = 0

    for booking in bookings:

        if booking.status != "Booked":
            continue

        revenue += booking.amount or 0

    revenue = round(revenue, 2)

    # -----------------------------
    # FIND BUSIEST SHOW
    # -----------------------------

    show_booking_count = {}

    for booking in bookings:

        if booking.status != "Booked":
            continue

        show_name = booking.show

        if show_name:
            show_booking_count[show_name] = (
                show_booking_count.get(show_name, 0) + 1
            )

    busiest_show = None
    busiest_count = 0

    for show_name, count in show_booking_count.items():

        if count > busiest_count:
            busiest_show = show_name
            busiest_count = count

    busiest_movie = None

    if busiest_show:

        busiest_movie = frappe.db.get_value(
            "Theatre Show",
            busiest_show,
            "movie_name",
            ignore_permissions=True
        )

    # -----------------------------
    # AI-STYLE INSIGHT
    # -----------------------------

    if occupancy >= 80:

        insight = (
            "Excellent booking activity. "
            "Most available seats are already booked."
        )

    elif occupancy >= 50:

        insight = (
            "Booking activity is moderate. "
            "Consider promoting upcoming shows."
        )

    else:

        insight = (
            "Booking activity is currently low. "
            "Consider promotional offers for upcoming shows."
        )

    return {
        "total_shows": len(shows),

        "running_shows": running,
        "upcoming_shows": upcoming,
        "completed_shows": completed,
        "cancelled_shows": cancelled,

        "total_bookings": total_bookings,
        "booked": booked,
        "cancelled_bookings": cancelled_bookings,

        "total_seats": total_seats,
        "occupancy": occupancy,

        "revenue": revenue,

        "busiest_movie": busiest_movie,
        "busiest_show_bookings": busiest_count,

        "insight": insight,

        "shows": shows,
        "show_occupancy": show_occupancy
    }


# ============================================================
# SIMPLE THEATRE CHATBOT
# ============================================================

@frappe.whitelist(allow_guest=True)
def theatre_chat(message):

    message = (message or "").strip().lower()

    if not message:
        return {
            "reply": "Please enter a question."
        }

    # Get all theatre information
    summary = theatre_ai_summary()

    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if message in [
        "hi",
        "hello",
        "hey",
        "hii",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        return {
            "reply": (
                "Hello! 👋 I am your Theatre Assistant. "
                "You can ask me about shows, bookings, "
                "revenue, occupancy, or the busiest movie."
            )
        }

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if "help" in message or "what can you do" in message:

        return {
            "reply": (
                "I can help you with:\n"
                "• Running shows\n"
                "• Upcoming shows\n"
                "• Completed shows\n"
                "• Cancelled shows\n"
                "• Booked tickets\n"
                "• Cancelled bookings\n"
                "• Revenue\n"
                "• Occupancy\n"
                "• Busiest movie\n"
                "• Theatre summary"
            )
        }

    # --------------------------------------------------------
    # RUNNING SHOWS
    # --------------------------------------------------------

    if "running" in message and "show" in message:

        return {
            "reply": (
                f"There are "
                f"{summary['running_shows']} running shows."
            )
        }

    # --------------------------------------------------------
    # UPCOMING SHOWS
    # --------------------------------------------------------

    if "upcoming" in message and "show" in message:

        return {
            "reply": (
                f"There are "
                f"{summary['upcoming_shows']} upcoming shows."
            )
        }

    # --------------------------------------------------------
    # COMPLETED SHOWS
    # --------------------------------------------------------

    if "completed" in message and "show" in message:

        return {
            "reply": (
                f"There are "
                f"{summary['completed_shows']} completed shows."
            )
        }

    # --------------------------------------------------------
    # CANCELLED SHOWS
    # --------------------------------------------------------

    if (
        "cancelled" in message
        and "show" in message
    ):

        return {
            "reply": (
                f"There are "
                f"{summary['cancelled_shows']} cancelled shows."
            )
        }

    # --------------------------------------------------------
    # CANCELLED BOOKINGS
    # --------------------------------------------------------

    if (
        ("cancelled" in message or "canceled" in message)
        and "booking" in message
    ):

        return {
            "reply": (
                f"There are "
                f"{summary['cancelled_bookings']} "
                f"cancelled bookings."
            )
        }

    # --------------------------------------------------------
    # BOOKED TICKETS
    # --------------------------------------------------------

    if (
        "booked" in message
        or "tickets booked" in message
        or "tickets are booked" in message
    ):

        return {
            "reply": (
                f"There are "
                f"{summary['booked']} booked tickets."
            )
        }

    # --------------------------------------------------------
    # TOTAL BOOKINGS
    # --------------------------------------------------------

    if (
        "total booking" in message
        or "total bookings" in message
    ):

        return {
            "reply": (
                f"There are "
                f"{summary['total_bookings']} total bookings."
            )
        }

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    if (
        "revenue" in message
        or "earning" in message
        or "earnings" in message
        or "income" in message
    ):

        return {
            "reply": (
                f"The current theatre revenue is "
                f"₹{summary['revenue']:.2f}."
            )
        }

    # --------------------------------------------------------
    # OCCUPANCY
    # --------------------------------------------------------

    if "occupancy" in message:

        return {
            "reply": (
                f"The overall theatre occupancy is "
                f"{summary['occupancy']}%."
            )
        }

    # --------------------------------------------------------
    # BUSIEST / POPULAR MOVIE
    # --------------------------------------------------------

    if (
        "busiest" in message
        or "most popular" in message
        or "popular movie" in message
    ):

        if summary["busiest_movie"]:

            return {
                "reply": (
                    f"The busiest movie is "
                    f"{summary['busiest_movie']} "
                    f"with "
                    f"{summary['busiest_show_bookings']} "
                    f"bookings."
                )
            }

        return {
            "reply": "There are no booked shows yet."
        }

    # --------------------------------------------------------
    # TOTAL SHOWS
    # --------------------------------------------------------

    if (
        "total show" in message
        or "total shows" in message
        or "how many shows" in message
    ):

        return {
            "reply": (
                f"There are "
                f"{summary['total_shows']} total shows."
            )
        }

    # --------------------------------------------------------
    # AVAILABLE SEATS
    # --------------------------------------------------------

    if (
        "available seats" in message
        or "seats available" in message
    ):

        total_available = sum(
            show["available_seats"]
            for show in summary["show_occupancy"]
        )

        return {
            "reply": (
                f"There are approximately "
                f"{total_available} available seats "
                f"across all shows."
            )
        }

    # --------------------------------------------------------
    # SHOW-WISE OCCUPANCY
    # --------------------------------------------------------

    if (
        "show occupancy" in message
        or "occupancy of each show" in message
        or "occupancy for each show" in message
    ):

        if not summary["show_occupancy"]:

            return {
                "reply": "There are no shows available."
            }

        response = "Show-wise occupancy:\n"

        for show in summary["show_occupancy"]:

            response += (
                f"• {show['movie_name']}: "
                f"{show['occupancy']}% "
                f"({show['booked_seats']}/"
                f"{show['total_seats']} booked)\n"
            )

        return {
            "reply": response
        }

    # --------------------------------------------------------
    # SUMMARY / REPORT
    # --------------------------------------------------------

    if (
        "summary" in message
        or "report" in message
        or "overview" in message
    ):

        return {
            "reply": (
                "🎬 Theatre Summary\n\n"
                f"Total Shows: {summary['total_shows']}\n"
                f"Running Shows: {summary['running_shows']}\n"
                f"Upcoming Shows: {summary['upcoming_shows']}\n"
                f"Completed Shows: {summary['completed_shows']}\n"
                f"Cancelled Shows: {summary['cancelled_shows']}\n\n"
                f"Total Bookings: {summary['total_bookings']}\n"
                f"Booked Tickets: {summary['booked']}\n"
                f"Cancelled Bookings: "
                f"{summary['cancelled_bookings']}\n\n"
                f"Revenue: ₹{summary['revenue']:.2f}\n"
                f"Occupancy: {summary['occupancy']}%\n\n"
                f"Busiest Movie: "
                f"{summary['busiest_movie'] or 'None'}\n\n"
                f"Insight: {summary['insight']}"
            )
        }

    # --------------------------------------------------------
    # DEFAULT RESPONSE
    # --------------------------------------------------------

    return {
        "reply": (
            "Sorry, I didn't understand that. 😕\n\n"
            "You can ask questions like:\n"
            "• How many shows are running?\n"
            "• How many tickets are booked?\n"
            "• What is the revenue?\n"
            "• What is the occupancy?\n"
            "• Which movie is busiest?\n"
            "• How many seats are available?\n"
            "• Give me a summary"
        )
    }
