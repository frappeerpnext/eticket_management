# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from urllib.request import ftpwrapper
from frappe.model.document import Document

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




		