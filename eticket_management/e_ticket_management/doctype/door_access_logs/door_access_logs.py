# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import json
from py_linq import Enumerable
from types import SimpleNamespace


class DoorAccessLogs(Document):
	def validate(self):
		if self.is_new():
			if self.id:
				if frappe.db.exists("Door Access Logs", {"id": self.id}):
					frappe.throw(
						_("Door Access Log id {} already exist".format(self.id))
					)
		self.posting_date = self.transaction_date
		
			
		
	def after_insert(self):
		if frappe.db.exists("POS Ticket",{"ticket_number":self.card_number,"is_checked_in":0}):
			
			frappe.db.sql("update `tabPOS Ticket` set checked_in_time=%s, is_checked_in=1 where is_checked_in = 0 and ticket_number =%s",	(self.transaction_date,self.card_number))
			frappe.db.commit()
		#update ticket total check in history
	 
		if self.status == "Success":
			if frappe.db.exists("Ticket Code",self.card_number, cache=True):
				doc = frappe.get_doc("Ticket Code",self.card_number)
				if doc:
					
					doc.total_checked_in = (doc.total_checked_in or 0) + 1
					doc.last_checked_in_date = self.transaction_date
					doc.save()
					frappe.db.commit()
			#generate Door Access Logs From Master Ticket
			if self.is_master:
				frappe.enqueue('eticket_management.e_ticket_management.doctype.door_access_logs.door_access_logs.generate_door_access_log_from_master', queue='long',self=self)
			

def generate_door_access_log_from_master(self):
	#Generate from POS
	if self.pos_invoice_id :
		sql = """SELECT 
					ticket_number FROM `tabPOS Ticket` a 
				WHERE a.pos_invoice_id = '{0}' AND 
					a.is_master_ticket_number = 0 AND 
					a.ticket_number NOT IN 
						(
							SELECT 
								card_number 
							FROM `tabDoor Access Logs` b 
							WHERE 
								b.pos_invoice_id = '{0}'
						)""".format(self.pos_invoice_id)
		pos_tickets = frappe.db.sql(sql, as_dict=1)
		for t in pos_tickets:
			doc = frappe.new_doc("Door Access Logs")
			doc.pos_invoice_id = self.pos_invoice_id
			doc.posting_date = self.posting_date
			doc.door_name = self.door_name
			doc.direction = self.direction
			doc.ip_address = self.ip_address
			doc.transaction_date = self.transaction_date
			doc.status = self.status
			doc.is_master = 0
			doc.card_number = t.ticket_number 
			doc.save()
		frappe.db.commit()
	else:
		sql = """SELECT 
  					a.ticket_number 
       			FROM `tabBooking Active Ticket` a 
				WHERE a.parent = '{0}' and 
    				a.is_master_ticket = 0  and 
         			a.ticket_number not in 
						(
							select 
								card_number 
							from 
								`tabDoor Access Logs` b 
							where 
								b.booking_number='{0}'
						)""".format(self.booking_number)
		
		pos_tickets = frappe.db.sql(sql, as_dict=1)
		for t in pos_tickets:
			doc = frappe.new_doc("Door Access Logs")
			doc.booking_number = self.booking_number
			doc.posting_date = self.posting_date
			doc.door_name = self.door_name
			doc.direction = self.direction
			doc.ip_address = self.ip_address
			doc.transaction_date = self.transaction_date
			doc.status = self.status
			doc.is_master = 0
			doc.card_number = t.ticket_number
			doc.save()
		frappe.db.commit()
