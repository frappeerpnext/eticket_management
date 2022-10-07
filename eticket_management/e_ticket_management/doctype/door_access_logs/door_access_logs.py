# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DoorAccessLogs(Document):
	def after_insert(self):
		if frappe.db.exists("POS Ticket",{"ticket_number":self.card_number,"is_checked_in":0}):
			
			frappe.db.sql("update `tabPOS Ticket` set checked_in_time=%s, is_checked_in=1 where is_checked_in = 0 and ticket_number =%s",	(self.transaction_date,self.card_number))

		#update ticket total check in history
	 
		if self.status == "Success":
			if frappe.db.exists("Ticket Code",self.card_number, cache=True):
				doc = frappe.get_doc("Ticket Code",self.card_number)
				if doc:
					
					
					doc.total_checked_in = (doc.total_checked_in or 0) + 1
					doc.last_checked_in_date = self.transaction_date
					doc.save()
					frappe.db.commit()




		
