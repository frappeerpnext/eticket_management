// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

 
frappe.ui.form.on('Ticket Booking', {
	
	refresh: function(frm) {
		frm.add_custom_button(__('Activate To Door Access Log'),function(){
			
			generateDoorAccessLog(frm)
		});
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
		
	},
	scan_ticket_number(frm) {  
		if(frm.doc.tickets_number==undefined){
			let entry = frm.add_child("tickets_number");
			entry.arrival_date = frm.doc.arrival_date; 
			entry.ticket_number = frm.doc.scan_ticket_number;  
			entry.master_ticket_number = frm.doc.master_ticket_number;  
			frm.refresh_field("tickets_number");
			
			frm.doc.scan_ticket_number = "";
			frm.refresh_field('scan_ticket_number'); 
			frappe.show_alert("Ticket Number: " + entry.ticket_number + " Added. Total Ticket Scan: " + frm.doc.tickets_number.length);
		}else{
			if(frm.doc.tickets_number.length<frm.doc.total_ticket){ 
				var _ticket_number_exsits = "0";
				for(var a in frm.doc.tickets_number){
					var data = frm.doc.tickets_number[a];
					if(data.ticket_number==frm.doc.scan_ticket_number){
						_ticket_number_exsits = "1";
					} 
				}
				if(_ticket_number_exsits=="0"){ 
					let entry = frm.add_child("tickets_number"); 
					entry.arrival_date = frm.doc.arrival_date;
					entry.ticket_number = frm.doc.scan_ticket_number;
					entry.master_ticket_number = frm.doc.master_ticket_number;
					frm.refresh_field("tickets_number");
					
					frm.doc.scan_ticket_number = "";
					frm.refresh_field('scan_ticket_number');
	
					frappe.show_alert("Ticket Number: " + entry.ticket_number + " Added. Total Ticket Scan: " + frm.doc.tickets_number.length + " of " + frm.doc.total_ticket);
					
				}else{
					frm.doc.scan_ticket_number = "";
					frm.refresh_field('scan_ticket_number');
				 
					frappe.show_alert({message:"Ticket Number: " + frm.doc.scan_ticket_number + " already exists.", indicator:"orange"});
					
				}
			}
			else{
				frm.refresh_field("tickets_number");
				frm.doc.scan_ticket_number = "";
				frm.refresh_field('scan_ticket_number');
			
				frappe.show_alert({message:"Tickets number be cannot greater than total tickets.", indicator:"orange"});
			}
		}   
	},
	master_ticket_number(frm){
		var _is_success = "0";
		var _is_remove_master = "0";
		var _ticket_number ="";
		if(frm.doc.tickets_number!=undefined){	 
			if(frm.doc.master_ticket_number!=""){
				for(var a in frm.doc.tickets_number){
					var data = frm.doc.tickets_number[a];  
					if(data.ticket_number==frm.doc.master_ticket_number){ 
						_ticket_number =data.ticket_number;
						_is_success = "1";	  
					}	 	
				} 
			}
			else{
				_is_remove_master = "1";
			}
		}
		if(_is_success=="0"){ 
			_is_remove_master = "1";
		}
		if(_is_remove_master=="1"){
			if(frm.doc.master_ticket_number!=""){
				frm.doc.master_ticket_number = ""; 
				frappe.show_alert({message:"There isn't ticket number for assign to master.", indicator:"orange"});
			} else{
				frappe.show_alert("Ticket number was unassigned from master");
			}
			for(var a in frm.doc.tickets_number){
				var data = frm.doc.tickets_number[a]; 
				data.is_master_ticket = 0;	 
				data.master_ticket_number = ""; 
			} 

		}else{
			if(_is_success=="1"){ 
				for(var a in frm.doc.tickets_number){
					var data = frm.doc.tickets_number[a];  
					if(data.ticket_number==frm.doc.master_ticket_number){
						_ticket_number =data.ticket_number; 
						data.is_master_ticket = 1;	
						data.master_ticket_number = ""; 
					}	else{
						data.is_master_ticket = 0;	 
						data.master_ticket_number = _ticket_number;
					}			
				}  
				frappe.show_alert("Ticket Number: " + _ticket_number + " is assign to master.");	
			}else{
			 
				frappe.show_alert({message:"There isn't ticket number for assign to master.", indicator:"orange"});
			
			}
		} 

		frm.refresh_field("tickets_number"); 
		frm.doc.master_ticket_number =(frm.doc.master_ticket_number==""?"":(_is_success=="1"?frm.doc.master_ticket_number:""));

		frm.refresh_field('master_ticket_number');	  	
	
	},

	arrival_date(frm){
		for(var a in frm.doc.tickets_number){
			var data = frm.doc.tickets_number[a]; 
			data.arrival_date = frm.doc.arrival_date;	  
		}  
		frm.refresh_field("tickets_number");
	},
	
	scan_remove_ticket_number(frm){
		let all_rows = frm.fields_dict["tickets_number"].grid.grid_rows.filter(function(d)
  		{ return  d.doc.is_checked==0 && d.doc.ticket_number == frm.doc.scan_remove_ticket_number});
		if(all_rows.length>0){
			frm.doc.scan_remove_ticket_number="";
			frm.refresh_field('scan_remove_ticket_number');	  
			if(frappe.user.has_role("eTicket Manager") == undefined){
				frappe.throw(__("Cannot remove ticket already checked in"));
			}
		}else{
			frappe.show_alert({message:"Ticket #:"  + frm.doc.scan_remove_ticket_number + "  does not exist.", indicator:"red"});
			frm.doc.scan_remove_ticket_number="";
			frm.refresh_field('scan_remove_ticket_number');
			return;
		}



		if (frm.doc.scan_remove_ticket_number==frm.doc.master_ticket_number){
			frappe.show_alert({message:"You cannot remove master ticket number.", indicator:"red"});
			frm.doc.scan_ticket_number = "";
			frm.refresh_field('scan_ticket_number');
			return;	
		}
		frm.get_field("tickets_number").grid.grid_rows[all_rows[0].doc.idx - 1].remove();
		frappe.show_alert("Ticket #:"  + frm.doc.scan_remove_ticket_number + " Removed");
		frm.refresh_field("tickets_number");

	
		
		frm.doc.scan_remove_ticket_number="";
		frm.refresh_field('scan_remove_ticket_number');	  	
	}


});

 
function generateDoorAccessLog(frm){
	
	if(frm.doc.total_ticket != frm.doc.tickets_number.length){
		frappe.throw(__("Please activate all ticket before activate to door access logs."))
	}
	if (frm.is_dirty()) {
		frappe.throw({message:__("Please save booking before activate to door access log"),title:__("Validate")})
		
	}else{
		frappe.confirm(
			__("Are you sure activate to door access?"),
			function(){
				
				frm.call({
					method: 'generate_door_access_log',
					doc:frm.doc,
					callback:function(r){
						if(r.message =='Success'){
							frappe.show_alert({message:__('Activated to door access log successfully.'),indicator:'green'})
						}else{
							frappe.show_alert({message:__('Activated to door access log failed.')},5)
						}
						
					},
					freeze: true,
					freeze_message: __('Activating To Door Access Log, Please wait.'),
					async: true,
				});
			},
		)
	}
	
	
}

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
				updateSumTotal(frm);
				
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
frappe.ui.form.on('Booking Active Ticket', {

    before_tickets_number_remove: function(frm, cdt, cdn){
		
		const row = locals[cdt][cdn];
		if(row.is_checked == 1){
			if(frappe.user.has_role('eTicket Manager') == undefined){
				frappe.throw(__("Cannot remove ticket already checked in." +"Row number:"+ row.idx + " ,Ticket Number:"+ row.ticket_number));
			}
		}
		
	},


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

