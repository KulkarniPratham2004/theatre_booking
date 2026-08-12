import frappe
import json


def create_theatre_booking_dashboard():
    dashboard_name = "Theatre Booking Dashboard"
    chart_name = "Theatre Shows by Status"

    # ---------------------------------------------------------
    # 1. Create Dashboard Chart
    # ---------------------------------------------------------

    if not frappe.db.exists("Dashboard Chart", chart_name):

        chart = frappe.get_doc({
            "doctype": "Dashboard Chart",
            "chart_name": chart_name,
            "chart_type": "Group By",
            "document_type": "Theatre Show",
            "group_by_type": "Count",
            "group_by_based_on": "custom_status",
            "type": "Donut",
            "filters_json": json.dumps({}),
            "is_public": 1,
            "module": "Theatre Booking"
        })

        chart.insert(ignore_permissions=True)

    # ---------------------------------------------------------
    # 2. Create Dashboard
    # ---------------------------------------------------------

    if not frappe.db.exists("Dashboard", dashboard_name):

        dashboard = frappe.get_doc({
            "doctype": "Dashboard",
            "dashboard_name": dashboard_name,
            "module": "Theatre Booking",
            "is_default": 1,
            "is_standard": 1,
            "charts": [
                {
                    "chart": chart_name,
                    "width": "Half"
                }
            ]
        })

        dashboard.insert(ignore_permissions=True)

    else:

        dashboard = frappe.get_doc(
            "Dashboard",
            dashboard_name
        )

        existing_charts = [
            row.chart for row in dashboard.charts
        ]

        if chart_name not in existing_charts:

            dashboard.append(
                "charts",
                {
                    "chart": chart_name,
                    "width": "Half"
                }
            )

            dashboard.save(ignore_permissions=True)

    frappe.db.commit()

    print("Theatre Booking Dashboard created successfully.")
