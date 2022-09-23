// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ticket Booking', {
	 refresh: function(frm) {
		frm.set_intro('Please set the value of description', 'blue');
	 }
});
