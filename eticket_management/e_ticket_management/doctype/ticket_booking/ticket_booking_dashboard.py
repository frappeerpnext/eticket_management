from frappe import _


def get_data():
	return {
		"fieldname": "booking_number",
	
		"transactions": [
			{"label": _("Groups"), "items": ["POS Ticket"]},
		
		],
	}
