frappe.views.calendar["Ticket Booking"] = {
	field_map: {
		"start": "booking_date",
		"end": "booking_date",
		"title": "name",
	},
	get_css_class: function(data) {
        console.log(data);
		if(data.status=="Closed") {
			return "success";
		} else{
        }
	}

};


