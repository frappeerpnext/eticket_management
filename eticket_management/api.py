import frappe
from frappe.utils import today


@frappe.whitelist()
def get_total_ticket_booking_forcast():
	data = frappe.db.sql("select sum(total_amount) as amount from `tabTicket Booking` where booking_date>= %s",today(),as_dict=True)
	if(data):
		return  {
			"value": data[0].amount,
			"fieldtype": "Currency"
		}
	
	return {
			"value": 0,
			"fieldtype": "Currency"
		}
 
 