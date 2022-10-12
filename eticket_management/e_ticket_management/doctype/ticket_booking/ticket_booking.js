// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ticket Booking', {
	 refresh: function(frm) {
		
	 }
});

frappe.ui.form.on('Booking Ticket Items', {
	quantity(frm,cdt, cdn) {
		let doc=   locals[cdt][cdn];
		doc.amount=doc.quantity*doc.price;
	    frm.refresh_field('ticket_items');
		updateSumTotal(frm);
	},
	
    price(frm,cdt, cdn) {
		let doc=   locals[cdt][cdn];
		doc.amount=doc.quantity*doc.price;
	    frm.refresh_field('ticket_items');
		updateSumTotal(frm);
	},
	ticket_items_add: updateSumTotal,
    ticket_items_remove: updateSumTotal,
})

function updateSumTotal(frm) {
    let sum_total = 0;
	let total_qty = 0;
	let total_ticket = 0;
	let total_ticket_amount = 0;

    $.each(frm.doc.ticket_items, function(i, d) {
        sum_total += flt(d.amount);
		total_qty +=flt(d.quantity);
		if (d.is_ticket)
			total_ticket += flt(d.quantity);
			total_ticket_amount += flt(d.amount)
    });
	
 
    frm.set_value('total_amount', sum_total);
    frm.set_value('total_quantity', total_qty);
    frm.set_value('total_ticket', total_ticket);
    frm.set_value('total_ticket_amount', total_ticket_amount);
	 
	frm.refresh_field("total_amount");
	frm.refresh_field("total_quantity");
	frm.refresh_field("total_ticket");
	frm.refresh_field("total_ticket_amount");
}

 