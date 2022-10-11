import frappe
from frappe.utils import today
@frappe.whitelist()
def get_ticket_booking_forcast():
    return 100