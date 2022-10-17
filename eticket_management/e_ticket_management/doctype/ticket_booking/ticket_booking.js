// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ticket Booking', {
	 refresh: function(frm) {
		frm.set_query("price_list", function() {
			return {
				"filters": {
					"selling": 1,
				}
			};
		});
	 },
	 price_list(frm) {
		update_item_price(frm)
	},
	customer(frm) {
		frappe.db.get_doc('Customer', frm.doc.customer)
		.then(doc => {
			frm.set_value('price_list', doc.default_price_list);  
			frm.refresh_field("price_list");
			update_item_price(frm)
		})
		
	}
});


 


frappe.ui.form.on('Booking Ticket Items', {
	ticket_type(frm,cdt, cdn) {
		var price_list = frm.doc.price_list;
		let doc=   locals[cdt][cdn];
		if (!frm.doc.price_list){
			price_list = "Standard Selling";
		}
		
		frappe.call({
			method: 'eticket_management.e_ticket_management.doctype.ticket_booking.ticket_booking.get_item_price',
			args: {
				price_list: price_list,
				item_code: doc.ticket_type
			},
			callback: (r) => {
				
				doc.price = r.message;
				doc.amount=doc.quantity*doc.price;
				frm.refresh_field('ticket_items');
				
			},
			error: (r) => {
				
			}
		})
	},
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
		if (d.is_ticket){ 
			total_ticket += flt(d.quantity);
			total_ticket_amount += flt(d.amount);
		}
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


function update_item_price(frm){
	let price_list = frm.doc.price_list;
	if (!frm.doc.price_list){
		price_list = "Standard Selling"

	}
	$.each(frm.doc.ticket_items, function(i, d) {
		 if (d.ticket_type){ 
		
		frappe.call({
			method: 'eticket_management.e_ticket_management.doctype.ticket_booking.ticket_booking.get_item_price',
			args: {
				price_list: frm.doc.price_list,
				item_code: d.ticket_type
			},
			callback: (r) => {
				d.price = r.message;
				d.amount=d.quantity*d.price;
				frm.refresh_field('ticket_items');
				updateSumTotal(frm);
			},
			error: (r) => {
				
			}
		})
	}
	});
	
}