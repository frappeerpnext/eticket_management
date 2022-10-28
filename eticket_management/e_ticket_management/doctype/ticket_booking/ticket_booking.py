# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from urllib.request import ftpwrapper
from frappe.model.document import Document
from frappe import _, msgprint
from frappe.utils import fmt_money,format_date
from frappe.utils.data import flt
from py_linq import Enumerable
class TicketBooking(Document):
	def validate(self):
		total_quantity = 0
		total_amount = 0
		for d in self.ticket_items:
			d.amount = d.price * d.quantity
			total_quantity = total_quantity + d.quantity
			total_amount = total_amount + d.amount

		self.total_quantity =total_quantity
		self.total_amount=total_amount
		self.keyword = str(self.customer) + " " + str(self.phone_number) + " " + str(self.email_address or "")
		
		self.calendar_title = """%s by: %s 
								Total Ticket:%s Amount:%s arrive on %s""" %(str(self.name),str(self.customer),str(self.total_ticket),str(fmt_money(self.total_ticket_amount,2,"USD","###,###.##")),str(format_date(self.arrival_date)))
		
	def on_submit(self):
		
		for t in self.ticket_items:
			for n in range(t.quantity):
				doc = frappe.get_doc(
					{
						"booking_number":self.name,
						"customer":self.customer,
						"transaction_date":self.booking_date,
						"item_code": t.ticket_type,
						"item_name": t.ticket_name,
						"price": t.price,
						"ticket_number": "N/A",
						"is_synced": 0,
						"is_can_sync": 1,
						"is_master_ticket_number": 0,
						"is_checked_in": 0,
						"doctype": "POS Ticket",
					}
				)
				doc.insert()

	def before_cancel(self):
		data = frappe.db.get_list('POS Ticket',
				filters={
					'booking_number': self.name,
					'is_checked_in':1
				}
			)
		if data:
			frappe.throw("You cannot cancel this booking because it is already checked in.")

	def on_cancel(self):
		 
		frappe.db.sql("update `tabPOS Ticket` set status = 'Cancel' where booking_number='{}'".format(self.name))
		frappe.db.commit()
		
	# def on_update_after_submit(self):

	# 	frappe.db.sql("delete from `tabPOS Ticket` where booking_number='{}'".format(self.name))
	# 	frappe.db.commit()
	# 	for t in self.ticket_items:
	# 		if t.is_ticket == 1:
	# 			for n in range(t.quantity):
	# 				doc = frappe.get_doc(
	# 					{
	# 						"booking_number":self.name,
	# 						"customer":self.customer,
	# 						"transaction_date":self.booking_date,
	# 						"item_code": t.ticket_type,
	# 						"item_name": t.ticket_name,
	# 						"price": t.price,
	# 						"ticket_number": "N/A",
	# 						"is_synced": 0,
	# 						"is_can_sync": 1,
	# 						"is_master_ticket_number": 0,
	# 						"is_checked_in": 0,
	# 						"doctype": "POS Ticket",
	# 					}
	# 				)
	# 				doc.insert()
			
	
	# def before_update_after_submit(self):
	# 	data = frappe.db.get_list('POS Ticket',
	# 			filters={
	# 				'booking_number': self.name,
	# 				'is_checked_in':1
	# 			}
	# 		)
	# 	if data:
	# 		frappe.throw("You cannot update this booking because it is already checked in.")
@frappe.whitelist()
def get_item_price(price_list, item_code):
	price = frappe.db.get_value("Item Price", [{'price_list':price_list},{'item_code':item_code}],"price_list_rate")
	if price:
		return price
	else:
		return 0
