// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense', {
	// refresh: function(frm) {

	// }
	
	
});

frappe.ui.form.on('Expense Item', {
	quantity(frm,cdt, cdn) {
		let doc= locals[cdt][cdn];
		doc.amount=doc.quantity*doc.price;
		frm.refresh_field('expense_item');
		updateSumTotal(frm);
	},
	
	price(frm,cdt, cdn) {
		let doc= locals[cdt][cdn];
		doc.amount=doc.quantity*doc.price;
		frm.refresh_field('expense_item');
		updateSumTotal(frm);
	},
})

function updateSumTotal(frm) {
    let sum_total = 0;
	let total_qty = 0;

    $.each(frm.doc.expense_item, function(i, d) {
        sum_total += flt(d.amount);
		total_qty +=flt(d.quantity);
    });
	
 
    frm.set_value('total_amount', sum_total);
    frm.set_value('total_quantity', total_qty);
	 
	frm.refresh_field("total_amount");
	frm.refresh_field("total_quantity");
}
