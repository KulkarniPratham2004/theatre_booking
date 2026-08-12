
import frappe
import json


def execute():
    chart_name = "Theatre Show Status"

    if frappe.db.exists("Dashboard Chart", chart_name):
        return

    chart = frappe.get_doc({
        "doctype": "Dashboard Chart",
        "chart_name": chart_name,
        "chart_type": "Group By",
        "document_type": "Theatre Show",
        "group_by_based_on": "custom_status",
        "group_by_type": "Count",
        "type": "Donut",
        "is_public": 1,
        "filters_json": json.dumps([]),
    })

    chart.insert(ignore_permissions=True)
    