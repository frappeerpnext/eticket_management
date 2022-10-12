frappe.views.calendar["Ticket Booking"] = {
	discbled:1,
	field_map: {
		"start": "booking_date",
		"end": "booking_date",
		"title": "calendar_title",
	},
	get_css_class: function(data) {
        console.log(data);
		if(data.status=="Closed") {
			return "success";
		} else{
        }
	}

};


