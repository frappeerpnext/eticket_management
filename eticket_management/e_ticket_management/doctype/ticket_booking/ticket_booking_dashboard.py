from frappe import _


def get_data():
	return {
		"fieldname": "booking_number",
	
		"transactions": [
			{"label": _("Issue Invoice"), "items": ["Sales Invoice"]},
			{"label": _("Door Access Logs"), "items": ["Door Access Logs"]},
		],
	}
