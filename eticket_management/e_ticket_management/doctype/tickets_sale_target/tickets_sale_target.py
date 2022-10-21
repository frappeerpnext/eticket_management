# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from datetime import date
from frappe.utils.data import today
import string
import datetime
from frappe import msgprint, throw
import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date

class TicketsSaleTarget(Document):
	def validate(self):
		years = [2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040]
		if not self.year in years:
			frappe.throw("Please enter a valid year")

		if self.is_new():
			if frappe.db.exists("Tickets Sale Target", {"year":self.year}):
				frappe.throw("Year {} already exist.".format(self.year))

		start_date = '{}-01-01'.format(self.year)
		end_date = '{}-12-31'.format(self.year)

		
		
		if self.tickets_sale_target_date:
			if not self.tickets_sale_target_date[0].target == self.daily_target:
				self.tickets_sale_target_date = []

		if self.tickets_sale_target_date or len(self.tickets_sale_target_date) == 0:
			dates = frappe.db.sql("select date from `tabDates` where date between '{}' and '{}'".format(start_date, end_date))
			for d in dates:
				self.append("tickets_sale_target_date",{"date":d,"target":self.daily_target})

		
	 

 
	