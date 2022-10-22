from importlib.metadata import files
import frappe
from frappe.utils import date_diff, is_git_url 
from frappe.utils.data import strip

def execute(filters=None): 
	if filters.filter_based_on =="Fiscal Year":
		filters.start_date = '{}-01-01'.format(filters.from_fiscal_year)
		filters.end_date = '{}-12-31'.format(filters.from_fiscal_year) 

	validate(filters)
 

	report_data = []
	skip_total_row=False
	message=None


	report_data = get_report_row_group_data(filters)
	skip_total_row = True
	if filters.row_group =="Row Group By":
		skip_total_row = False


	report_chart = None
	if filters.chart_type !="None" and len(report_data)<=100:
		report_chart = get_report_chart(filters,report_data) 
	 
	return get_columns(filters), report_data,message, report_chart, get_report_summary(report_data,filters),skip_total_row
	#return get_columns(filters), report_data, message, report_chart, get_report_summary(report_data,filters),skip_total_row
 
def validate(filters):
	
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:

			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))

	
	if filters.column_group=="Daily":
		n = date_diff(filters.end_date, filters.start_date)
		if n>30:
			frappe.throw("Date range cannot greater than 30 days")

	if filters.row_group and filters.parent_row_group:
		if(filters.row_group == filters.parent_row_group):
			frappe.throw("Parent row group and row group can not be the same")
 

def get_columns(filters):
	
	columns = []
	columns.append({'fieldname':'row_group','label':filters.row_group,'fieldtype':'Data','align':'left','width':300})
	fields = get_report_field(filters)
	for f in fields:
		columns.append({
				'fieldname': f['fieldname'],
				'label': f["label"],
				'fieldtype':f['fieldtype'],
				'precision': f["precision"],
				'align':f['align'],
				'width':f['width']
				}
			)
	return columns
 
def get_dynamic_columns(filters):
	hide_columns = filters.get("hide_columns")
	#dynmic report file
	fields = get_fields(filters)
	#static report field
	report_fields = get_report_field(filters)
	columns=[]
	for f in fields:
		for rf in report_fields:
			if not hide_columns or  rf["label"] not in hide_columns:
				columns.append({
					'fieldname':f["fieldname"] + "_" + rf["fieldname"],
					'label': f["label"] + " "  + rf["short_label"],
					'fieldtype':rf["fieldtype"],
					'precision': rf["precision"],
					'align':rf["align"]}
				)

		
	return columns

def get_fields(filters):
	sql=""
	
	if filters.column_group=="Daily":
		sql = """
			select 
				concat('col_',date_format(date,'%d_%m')) as fieldname, 
				date_format(date,'%d') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%d_%m')) , 
				date_format(date,'%d')  	
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group =="Monthly":
		sql = """
			select 
				concat('col_',date_format(date,'%m_%Y')) as fieldname, 
				date_format(date,'%b %y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%m_%Y')) , 
				date_format(date,'%b %y')  	
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Weekly":
		sql = """
			select 
				concat('col_',date_format(date,'%v_%Y')) as fieldname, 
				concat('WK ',date_format(date,'%v %y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%v_%Y')), 
				concat('WK ',date_format(date,'%v %y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Quarterly":
		sql = """
			select 
				concat('col_',QUARTER(date)) as fieldname, 
				concat('Q',QUARTER(date),' ',date_format(date,'%y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',QUARTER(date)),
				concat('Q',QUARTER(date),' ',date_format(date,'%y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Half Yearly":
		sql = """
			select 
				concat('col_',if(month(date) between 1 and 6,'jan_jun','jul_dec'),date_format(date,'%y')) as fieldname, 
				concat(if(month(date) between 1 and 6,'Jan-Jun','Jul-Dec'),' ',date_format(date,'%y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',if(month(date) between 1 and 6,'jan_jun','jul_dec'),date_format(date,'%y')), 
				concat(if(month(date) between 1 and 6,'Jan-Jun','Jul-Dec'),' ',date_format(date,'%y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Yearly":
		sql = """
			select 
				concat('col_',date_format(date,'%Y')) as fieldname, 
				date_format(date,'%Y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%Y')),
				date_format(date,'%Y')
		""".format(filters.start_date, filters.end_date)

	if sql=="":
		return None
	else:
		fields = frappe.db.sql(sql,as_dict=1)
		
		return fields
 
def get_conditions(filters,group_filter=None):
	conditions = ""

	start_date = filters.start_date
	end_date = filters.end_date

 
	if(group_filter!=None):
		conditions += " and {} ='{}'".format(group_filter["field"],group_filter["value"].replace("'","''").replace("%","%%"))

	conditions += "  a.transaction_date between '{}' AND '{}'".format(start_date,end_date)

	if filters.get("item_group"):
		conditions += " AND a.parent_item_group in %(item_group)s"

	if filters.get("item_category"):
		conditions += " AND a.item_group in %(item_category)s"

	if filters.get("customer_group"):
		conditions += " AND a.customer_group in %(customer_group)s"


	if filters.get("market_segment"):
		conditions += " AND a.market_segment in %(market_segment)s"

	if filters.get("business_source"):
		conditions += " AND a.business_source in %(business_source)s"
	
	return conditions

def get_report_row_group_data(filters):
	target_row_group = "date_format(d.date,'%%d-%%m-%%Y')"
	row_group = "date_format(t.transaction_date,'%%d-%%m-%%Y')"
 
	if filters.parent_row_group == "Month":
		row_group = "date_format(t.transaction_date,'%%m %%Y')"
		target_row_group = "date_format(d.date,'%%m %%Y')"
	
	if filters.parent_row_group == "Year":
		row_group = "date_format(t.transaction_date,'%%Y')"
		target_row_group = "date_format(d.date,'%%Y')"

	is_group = 1
	if  filters.row_group == "Row Group By":
		is_group = 0
	sql ="""
		with a as (
			select 
				{0} as row_group,
				min(d.date) as start_date,
				max(d.date) as end_date,
				sum(b.target) as target
			from `tabDates`  d inner join `tabTickets Sale Target Date` b on b.date = d.date
			where
			d.date between %(start_date)s and %(end_date)s
			group by
				{0}
		),b as (
			select 
				{1} as row_group,
				count(t.name) as total_sold_quantity,
				sum(t.price) as total_sold_amount
			from `tabPOS Ticket` t
			where
				t.status ='Active' and 
				t.transaction_date between %(start_date)s and %(end_date)s
			group by
				{1}
		)
		select 
			a.row_group,
			a.start_date,
			a.end_date,
			ifnull(b.total_sold_quantity,0) as total_sold_quantity,
			ifnull(b.total_sold_amount,0) as total_sold_amount,
			a.target as target_quantity,
			0 as occupancy,
			{2} as is_group,
			0 as indent
		from a left join b on b.row_group = a.row_group

	""".format(target_row_group, row_group, is_group)
	
	parent = frappe.db.sql(sql,filters, as_dict=1)
	data = []
	for p in parent:
		if p["target_quantity"] > 0:
			p["occupancy"] = (p["total_sold_quantity"] / p["target_quantity"]*100)
		
		data.append(p)
		if  filters.row_group != "Row Group By":
			children = get_report_data(filters,p["start_date"],p["end_date"])
			for c in children:
				data.append(c)

	return data
 


def get_report_data(filters, start_date, end_date):
	data = []
	row_group = [d for d in get_row_groups() if d["label"]==filters.row_group][0]
	sql ="""
		select 
			{0} as row_group, 
			count(name) as total_sold_quantity,
			sum(a.price) as total_sold_amount ,
			0 as target_quantity,
			1 as indent,
			0 as occupancy
		from `tabPOS Ticket` a 
		WHERE
			a.status = 'Active' and 
			a.transaction_date between '{1}'  and '{2}'   
			
		group by {0}
	""".format(row_group["fieldname"], start_date,end_date)
	data = frappe.db.sql(sql, as_dict=1)
	 
	return data
 
 
def get_report_summary(data,filters):
	report_summary=[]
	ticket_sold=sum(d["total_sold_quantity"] for d in data if d["indent"] ==0)
	report_summary.append({"label":"Total Ticket Sold","value":ticket_sold,"indicator":"green"})	

	value=sum(d["total_sold_amount"] for d in data if d["indent"] ==0)
	value = frappe.utils.fmt_money(value)
	report_summary.append({"label":"Total Amount","value":value,"indicator":"grey"})



	target_quantity=sum(d["target_quantity"] for d in data if d["indent"] ==0)
	report_summary.append({"label":"Total Target Quantity","value":target_quantity,"indicator":"red"})

 
	if target_quantity >0:
		report_summary.append({"label":"Total Occupany","value":"{:0.2%}".format(ticket_sold/target_quantity),"indicator":"red"})	
	else:
		report_summary.append({"label":"Total Occupany","value":"{:0.2%}".format(0),"indicator":"red"})	

		
	return report_summary

def get_report_chart(filters,data):
	columns = []
	dataset = []
	colors = []

	report_fields = get_report_field(filters)

	
	for d in data:
		if d["indent"] ==0:
			columns.append(d["row_group"])

	for rf in report_fields:
		fieldname = rf["fieldname"]
		if(fieldname=="total_sold_quantity"):
			dataset.append({'name':rf["label"],'values':(d["total_sold_quantity"] for d in data if d["indent"]==0)})
		elif(fieldname=="target_quantity"):
			dataset.append({'name':rf["label"],'values':(d["target_quantity"] for d in data if d["indent"]==0)})


	chart = {
		'data':{
			'labels':columns,
			'datasets':dataset
		},
		"type": filters.chart_type,
		"lineOptions": {
			"regionFill": 1,
		},
		"axisOptions": {"xIsSeries": 1}
	}
	return chart
  
def get_report_field(filters):
	
	return [
		{"label":"Ticket Sold Qty","short_label":"Qty", "fieldname":"total_sold_quantity","fieldtype":"Int","indicator":"Grey","precision":2, "align":"center","chart_color":"#468710","width":200},
		{"label":"Amount", "short_label":"Amt", "fieldname":"total_sold_amount","fieldtype":"Currency","indicator":"Red","precision":None, "align":"right","chart_color":"#2E7D32" ,"width":200},
		{"label":"Target Qty", "short_label":"Target qty", "fieldname":"target_quantity","fieldtype":"Int","indicator":"Grey","precision":None, "align":"center","chart_color":"#dd5574", "width":200},
		{"label":"Occupany", "short_label":"Occupany", "fieldname":"occupancy","fieldtype":"Percent","precision":None,"indicator":"Grey", "align":"center","chart_color":"#dd5574","width":200}
	]

def get_row_groups():
	return [
		{
			"fieldname":"coalesce(a.market_segment,'Not Set')",
			"label":"Market Segment",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"coalesce(a.market_source,'Not Set')",
			"label":"Market Source",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"coalesce(a.market_segment_type,'Not Set')",
			"label":"Market Segment Type",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"coalesce(a.market_source_type,'Not Set')",
			"label":"Market Source Type",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"a.item_group",
			"label":"Ticket Category",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"concat(ifnull(a.customer,'Not Set'),'-',a.customer_name)",
			"label":"Customer",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"a.customer_group",
			"label":"Customer Group",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"ifnull(a.Territory,'Not Set')",
			"label":"Nationality",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"date_format(a.transaction_date,'%%d/%%m/%%Y')",
			"label":"Date",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"date_format(a.transaction_date,'%%m/%%Y')",
			"label":"Month",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"date_format(a.transaction_date,'%%Y')",
			"label":"Year",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"concat(a.item_code, '-',a.item_name)",
			"label":"Ticket Type",
			
		}
	]