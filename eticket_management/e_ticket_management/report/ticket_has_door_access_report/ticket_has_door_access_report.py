# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns=[]
	columns.append({'fieldname':"ticket_number",'label':"Ticket Number",'fieldtype':'Data','align':'center','width':130})
	columns.append({'fieldname':"door_access_card_number",'label':"Door Access Number",'fieldtype':'Data','align':'center','width':160})
	columns.append({'fieldname':"reference",'label':"Ticket Reference",'fieldtype':'Data','align':'center','width':130})
	columns.append({'fieldname':"posting_date",'label':"Door Access Date",'fieldtype':'Data','align':'left','width':130})
	return columns

def get_data(filters):
	data = []
	sql = """
			select 
				a.ticket_number,
				coalesce(b.card_number,'No Door Access') door_access_card_number,
				ifnull(a.pos_document_number,c.document_number) as reference,
				coalesce(b.posting_date,'No Door Access') posting_date
			from `tabPOS Ticket` a
			left join `tabDoor Access Logs` b on b.card_number = a.ticket_number
			inner join `tabPOS Invoice` c on c.name = a.pos_invoice
			where a.transaction_date between '{0}' and '{1}'
			group by a.ticket_number
			UNION all
			select
				b.ticket_number,
				coalesce(card_number,'No Door Access') door_access_card_number,
				a.name as reference,
				coalesce(posting_date,'No Door Access') posting_date
			from `tabTicket Booking` a 
			left join `tabBooking Active Ticket` b on a.name = b.parent
			inner join `tabDoor Access Logs` c on c.card_number = b.ticket_number
			where b.arrival_date between '{0}' and '{1}'
			group by  b.ticket_number
	""".format(filters.start_date,filters.end_date)
	data = frappe.db.sql(sql,as_dict=1)
	return data