# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe import _
class POSTicket(Document):
	def validate(self):
		if self.is_new():
			if self.id:
				if frappe.db.exists("POS Ticket", {"id": self.id}):
					frappe.throw(
						_("POS Ticket id {} already exist".format(self.id))
					)

		#check pos invoice name
		if(frappe.db.exists("POS Invoice", {"id": self.pos_invoice_id})):
			pos_invoice,document_number =  frappe.db.get_value('POS Invoice', {'id': self.pos_invoice_id}, ['name','document_number'])
			if pos_invoice and document_number:
				self.pos_invoice = pos_invoice
				self.pos_document_number = document_number
		

