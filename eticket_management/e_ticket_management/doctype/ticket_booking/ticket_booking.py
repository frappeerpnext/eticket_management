# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from urllib.request import ftpwrapper
from frappe.model.document import Document
from frappe import _
from frappe.utils import fmt_money

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
		self.calendar_title = _("New Booking") + " " + str(self.name) + " " + str(self.customer) + _("Total Ticket") + str(self.total_ticket) + _("Total Amount") + fmt_money(self.total_ticket_amount,2,None,"###,###.##")

	def on_submit(self):
		
		for t in self.ticket_items:
			for n in range(t.quantity):
				doc = frappe.get_doc(
					{
						"booking_number":self.name,
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

