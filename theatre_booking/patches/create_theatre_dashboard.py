
import frappe


def execute():
    dashboard_name = "Theatre Booking Dashboard"

    if frappe.db.exists("Dashboard", dashboard_name):
        return

    dashboard = frappe.get_doc({
        "doctype": "Dashboard",
        "dashboard_name": dashboard_name,
        "module": "Theatre Booking",
        "is_default": 1,
        "is_standard": 0,
        "charts": [
            {
                "chart": "Theatre Show Status"
            }
        ],
    })

    dashboard.insert(ignore_permissions=True)
