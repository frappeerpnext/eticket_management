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
