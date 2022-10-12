# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff

def execute(filters=None):
	data=[]
	if filters.parent_row_group != "None":
		data = get_report_group_data(filters)
	else:
		data = get_data(filters)
	validate(filters)
	return get_columns(filters), data

def get_filters(filters):
	data = " transaction_date between '{}' AND '{}'".format(filters.start_date,filters.end_date)
	data = data + "{}={}".format()
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':"group_field",'label':"{}".format(filters.row_group),'fieldtype':'Data','align':'left','width':200})
	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
				columns.append({'fieldname':"qty_"+f['fieldname'],'label':"Total QTY " + f["label"],'align':'right','fieldtype':'Data'})
				columns.append({'fieldname':f['fieldname'],'label':"Total Amt " + f["label"],'align':'right','fieldtype':'Currency'})
	columns.append({'fieldname':"total_amount",'label':"Total Amount",'fieldtype':'Currency','align':'right','width':110})
	columns.append({'fieldname':"total_ticket",'label':"Total Ticket",'fieldtype':'Data','align':'center','width':100})
	return columns

def get_report_group_data(filters):
	parent = get_data(filters,0,get_row_group(filters.parent_row_group))
	data=[]
	for p in parent:
		p["is_group"] = 1
		data.append(p)
		children = get_data(filters, 1,get_row_group(filters.parent_row_group),parent["group_field"])
		for c in children:data.append(c)
	return data

def get_data(filters,indent=0,parent_row_group=""):
	row_group = ""
	if parent_row_group != "":
		row_group = parent_row_group
	else:
		row_group = get_row_group(filters.row_group)
	sql = "SELECT {} as group_field,{} as indent,".format(row_group,indent)
	data=[]
	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
			sql = sql +	"""
			SUM(if(transaction_date between '{0}' AND '{1}',{2},0)) as '{3}',
			sum(if(transaction_date between '{0}' AND '{1}',1,0)) as 'qty_{3}',
			""".format(f["start_date"],f["end_date"],"price",f["fieldname"])
	sql = sql + """
				sum(price) total_amount,
				count(name) total_ticket
				FROM `tabPOS Ticket` a
					WHERE {0}
				group by {1}
			""".format(get_filters(filters),row_group)
	frappe.msgprint(sql)
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data

def get_row_group(row_group):
	data= ""
	if(row_group) == "Item": data = "item_name"
	if(row_group) == "Sale Invoice": data = "pos_invoice"
	if(row_group) == "Cashier": data = "a.pos_username"
	return data

def validate(filters):

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))

	if filters.column_group=="Daily":
		n = date_diff(filters.end_date, filters.start_date)
		if n>30:
			frappe.throw("Date range cannot greater than 30 days")

def get_fields(filters):
	sql=""
	if filters.column_group=="Daily":
		sql = """
			select 
				concat(date_format(date,'%d_%m')) as fieldname, 
				date_format(date,'%d') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat(date_format(date,'%d_%m')) , 
				date_format(date,'%d')  	
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group =="Monthly":
		sql = """
			select 
				concat(date_format(date,'%m_%Y')) as fieldname, 
				date_format(date,'%b %y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat(date_format(date,'%m_%Y')) , 
				date_format(date,'%b %y')  	
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Yearly":
		sql = """
			select 
				concat(date_format(date,'%Y')) as fieldname, 
				date_format(date,'%Y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat(date_format(date,'%Y')),
				date_format(date,'%Y')
		""".format(filters.start_date, filters.end_date)
	fields = frappe.db.sql(sql,as_dict=1)
	return fields