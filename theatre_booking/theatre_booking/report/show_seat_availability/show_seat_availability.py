import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Show",
            "fieldname": "show_name",
            "fieldtype": "Link",
            "options": "Theatre Show",
            "width": 150,
        },
        {
            "label": "Movie Name",
            "fieldname": "movie_name",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": "Show Date",
            "fieldname": "show_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": "Show Time",
            "fieldname": "show_time",
            "fieldtype": "Time",
            "width": 100,
        },
        {
            "label": "Screen",
            "fieldname": "screen",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Total Seats",
            "fieldname": "total_seats",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Booked Seats",
            "fieldname": "booked_seats",
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "label": "Available Seats",
            "fieldname": "available_seats",
            "fieldtype": "Int",
            "width": 120,
        },
    ]


def get_data(filters=None):

    conditions = []
    values = {}

    if filters:

        if filters.get("show"):
            conditions.append("ts.name = %(show)s")
            values["show"] = filters.get("show")

        if filters.get("show_date"):
            conditions.append("ts.show_date = %(show_date)s")
            values["show_date"] = filters.get("show_date")

        if filters.get("movie_name"):
            conditions.append(
                "ts.movie_name LIKE %(movie_name)s"
            )
            values["movie_name"] = (
                "%" + filters.get("movie_name") + "%"
            )

    condition_sql = ""

    if conditions:
        condition_sql = " AND " + " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            ts.name AS show_name,
            ts.movie_name,
            ts.show_date,
            ts.show_time,
            ts.screen,
            ts.total_seats,

            COUNT(
                CASE
                    WHEN tb.status = 'Booked'
                    THEN tb.name
                END
            ) AS booked_seats

        FROM `tabTheatre Show` AS ts

        LEFT JOIN `tabTheatre Booking` AS tb
            ON tb.show = ts.name

        WHERE 1 = 1
        {condition_sql}

        GROUP BY
            ts.name,
            ts.movie_name,
            ts.show_date,
            ts.show_time,
            ts.screen,
            ts.total_seats

        ORDER BY
            ts.show_date,
            ts.show_time
        """,
        values,
        as_dict=True,
    )

    for row in data:
        row["available_seats"] = (
            row["total_seats"] - row["booked_seats"]
        )

    return data