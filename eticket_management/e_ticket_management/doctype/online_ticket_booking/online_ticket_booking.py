# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from pickle import TRUE
import frappe
from frappe.model.document import Document
from frappe.utils import flt


class OnlineTicketBooking(Document):
	def validate(self):
		if self.booking_items:
			for b in self.booking_items:
				b.amount = b.price * b.quantity

		self.total_quantity = sum(flt(d.quantity) for d in self.booking_items)
		self.total_amount = sum(flt(d.amount) for d in self.booking_items)
		total_ticket_items = filter(lambda t: t.is_ticket == TRUE, self.booking_items)
		#self.total_ticket = sum(flt(d.quantity) for d in total_ticket_items)
	#def after_insert(self):
		# self.booking_number = 'BK2022-000001'
		# self.save()
