from frappe import _


def get_data():
	return {
		"fieldname": "booking_number",
	
		"transactions": [
			{"label": _("Issue Invoice"), "items": ["Sales Invoice"]},
		],
	}
