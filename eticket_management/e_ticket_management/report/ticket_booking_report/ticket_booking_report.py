# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns=[]
	columns.append({'fieldname':"name",'label':"Document",'fieldtype':'Data','align':'center','width':125})
	columns.append({'fieldname':"booking_date",'label':"Booking Date",'fieldtype':'Date','align':'center','width':110})
	columns.append({'fieldname':"arrival_date",'label':"Arrival Date",'fieldtype':'Date','align':'center','width':110})
	columns.append({'fieldname':"customer",'label':"Customer",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':"total_ticket",'label':"Total Ticket",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':"total_ticket_amount",'label':"Total Amount",'fieldtype':'Data','align':'right','width':110})
	# columns.append({'fieldname':"business_source",'label':"Business Source",'fieldtype':'Data','align':'right','width':160})
	# columns.append({'fieldname':"business_source_type",'label':"Business Source Type",'fieldtype':'Data','align':'right','width':200})
	# columns.append({'fieldname':"market_segment",'label':"Market Segment",'fieldtype':'Data','align':'right','width':160})
	# columns.append({'fieldname':"marketing_segment_type",'label':"Marketing Segment Type",'fieldtype':'Data','align':'right','width':200})
	
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
	parent_data = []
	data= []
	parent = """
			SELECT 
				0 indent,
				1 is_group,
				booking_date,
				concat(customer,' / ',phone_number) customer,
				arrival_date,
				total_quantity,
				total_amount,
				is_checked_in,
				total_ticket,
				total_ticket_amount,
				business_source,
				market_segment,
				business_source_type,
				marketing_segment_type,
				name
			FROM `tabTicket Booking` {0}
	""".format(get_filters(filters))
	parent_data = frappe.db.sql(parent,as_dict=1)
	for dic_p in parent_data:
		child_data = ("""
						with sale as(SELECT
							a.item_group, 
							coalesce(a.supplier_name,'Not Set') supplier_name,
							a.item_code,
							a.item_name,
							a.stock_uom,
							concat('<img src=','''',a.image,'''',' Style="Height:100px" />') image,
							coalesce(SUM(a.qty * a.conversion_factor),0) sale_qty
						FROM `tabSales Invoice Item` a
							INNER JOIN `tabSales Invoice` b ON b.name = a.parent									
						WHERE {0} and a.item_group = '{4}'
						GROUP BY
							a.item_group, 
							a.supplier_name,
							a.item_code,
							a.item_name,
							a.stock_uom,
							a.image)

						SELECT 
							a.*,
							coalesce((SELECT 
									sum(qty_after_transaction) qty_after_transaction
									FROM  `tabStock Ledger Entry` c
									WHERE  concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')) =
									( SELECT  max(concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')))
											FROM  `tabStock Ledger Entry` d
											WHERE posting_date BETWEEN '{1}' AND '{2}' and d.item_code = c.item_code AND d.warehouse = if('{3}'='None',d.warehouse,'{3}')
									)
								and posting_date BETWEEN '{1}' AND '{2}' AND warehouse = if('{3}'='None',warehouse,'{3}') AND c.item_code = a.item_code),0) boh,
							coalesce((SELECT 
									sum(qty_after_transaction) qty_after_transaction
									FROM  `tabStock Ledger Entry` e
									WHERE  concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')) =
									( SELECT  max(concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')))
											FROM  `tabStock Ledger Entry` f
											WHERE posting_date BETWEEN '{1}' AND '{2}' and f.item_code = e.item_code AND f.warehouse = if('{3}'='None',f.warehouse,'{3}')
									)
								and posting_date BETWEEN '{1}' AND '{2}' AND warehouse = if('{3}'='None',warehouse,'{3}') AND e.item_code = a.item_code),0) - a.sale_qty total_qty
						FROM sale a
					""".format(get_filters(filters),filters.start_date,filters.end_date,filters.warehouse,dic_p["item_code"]))
		child = frappe.db.sql(child_data,as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"] = 0
			data.append(dic_c)

	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data