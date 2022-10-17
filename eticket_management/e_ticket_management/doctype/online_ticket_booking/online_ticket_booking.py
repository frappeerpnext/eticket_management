# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class OnlineTicketBooking(Document):
	def validate(self):
		total_quantity = 0
		if self.booking_items:
			for b in self.booking_items:
				b.amount = b.price * b.quantity
				total_quantity = total_quantity + b.quantity

		self.total_quantity = total_quantity

	def after_insert(self):
		self.booking_number = 'BK2022-000001'
		self.save()
