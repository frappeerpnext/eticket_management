# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns=[]
	columns.append({'fieldname':"name",'label':"Document",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"booking_date",'label':"Booking Date",'fieldtype':'Date','align':'right','width':110})
	columns.append({'fieldname':"customer",'label':"Customer",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"phone_number",'label':"Phone",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"arrival_date",'label':"Arrival Date",'fieldtype':'Date','align':'right','width':110})
	columns.append({'fieldname':"total_ticket",'label':"Total Ticket",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"total_ticket_amount",'label':"Total Amount",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"business_source",'label':"Business Source",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"business_source_type",'label':"Booking Date",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"market_segment",'label':"Booking Date",'fieldtype':'Data','align':'right','width':110})
	columns.append({'fieldname':"marketing_segment_type",'label':"Booking Date",'fieldtype':'Data','align':'right','width':110})
	
	return columns
def get_filters(filters):
	fil=""
	fil = "where booking_date between '{0}' and '{1}'".format(filters.start_date,filters.end_date)
	if(filters.market_segment):
		fil = fil + " and market_segment in (" + get_list(filters,"market_segment") + ")"
	if(filters.business_source):
		fil = fil + " and business_source in (" + get_list(filters,"business_source") + ")"
	return fil

def get_data(filters):
	data = []
	sql = """
			SELECT 
				booking_date,
				customer,
				phone_number,
				arrival_date,
				total_quantity,
				total_amount,
				is_checked_in,
				total_ticket,
				total_ticket_amount,
				business_source,
				market_segment,
				business_source_type,
				marketing_segment_type
				name
			FROM `tabTicket Booking` {0}
	""".format(get_filters(filters))
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data