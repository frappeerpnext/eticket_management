# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from py_linq import Enumerable


class OnlineTicketBooking(Document):
	def validate(self):
		if not frappe.db.exists("Territory", self.territory):
			territory = frappe.new_doc('Territory')
			territory.territory_name=self.territory
			territory.parent_territory = 'All Territories'
			territory.insert()
		for d in self.booking_items:
			d.amount = d.price * d.quantity
		self.total_quantity = sum(flt(d.quantity) for d in self.booking_items)
		self.total_amount = sum(flt(d.amount) for d in self.booking_items)
		total_ticket_items = Enumerable(self.booking_items).where(lambda x:x.is_ticket == 1)
		self.total_ticket = sum(flt(d.quantity) for d in total_ticket_items)
		self.total_ticket_amount = total_ticket_items.sum(lambda x:x.amount)

	def after_insert(self):
		customer_doc = frappe.get_doc({ 
			"doctype": "Customer",
			"customer_name": self.customer_name,
			"phone_number": self.phone_number,
			"customer_group": "Individual",
			"territory": self.territory,
			"email_address": self.email_address
		})
		customer_doc.insert()
		booking_doc = frappe.get_doc({
			"doctype": "Ticket Booking",
			"booking_date": self.booking_date,
			"total_ticket": self.total_ticket,
			"total_ticket_amount": self.total_ticket_amount,
			"arrival_date": self.arrival_date,
			"payment_amount": self.payment_amount,
			"customer": customer_doc.name,
			"ticket_items": self.booking_items,
		})
		booking_doc.insert()
		frappe.db.set_value('Online Ticket Booking', self.name, 'booking_number', booking_doc.name)
		frappe.db.commit()
