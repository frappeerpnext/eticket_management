frappe.listview_settings['POS Ticket'] = {
	get_indicator: function(doc) {
		// if (doc.booking_number && doc.is_checked_in) {
		// 	return [__("Checked In"), "green", "is_checked_in,=,Yes"];
		// } else if (doc.booking_number && doc.is_checked_in==0) {
		// 	return [__("Booked"), "orange", "is_checked_in,=,No"];
		// } 

        return [__("Checked In"), "green", "is_checked_in,=,Yes"];
	},

 
};
