import frappe
from frappe.utils import date_diff 
from frappe.utils.data import strip
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from decimal import Decimal, ROUND_HALF_UP
def execute(filters=None): 
	if filters.filter_based_on =="Fiscal Year":
		filters.start_date = '{}-01-01'.format(filters.from_fiscal_year)
		filters.end_date = '{}-12-31'.format(filters.from_fiscal_year) 

	validate(filters)
	#run this to update parent_item_group in table sales invoice item
	update_parent_item_group()
	update_sale() 

	report_data = []
	skip_total_row=False
	message=None
	if filters.get("parent_row_group"):
		report_data = get_report_group_data(filters)
		message="Enable <strong>Parent Row Group</strong> making report loading slower. Please try  to select some report filter to reduce record from database "
		skip_total_row = True
	else:
		report_data = get_report_data(filters) 
	report_chart = None
	if filters.chart_type !="None" and len(report_data)<=100:
		report_chart = get_report_chart(filters,report_data) 
	return get_columns(filters), report_data, message, report_chart, get_report_summary(report_data,filters),skip_total_row
 
def validate(filters):
	if not filters.department:
		filters.department = frappe.db.get_list("Department",pluck='name')

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
 
def update_parent_item_group():
	frappe.db.sql(
		"""
			UPDATE `tabSales Invoice Item` a 
			SET parent_item_group = (
					SELECT parent_item_group FROM `tabItem Group` WHERE NAME=a.item_group) 
			WHERE ifnull(parent_item_group,'') = ''
		"""
	)

def update_sale():
	frappe.db.sql(
		"""
			UPDATE `tabSales Invoice Item` a 
			SET parent_item_group = (
					SELECT parent_item_group FROM `tabItem Group` WHERE NAME=a.item_group) 
			WHERE ifnull(parent_item_group,'') = ''
		"""
	)

	#update transaction to tbl sale invoice item
	sale_invoices = frappe.db.sql("select distinct parent from `tabSales Invoice Item` where total_transaction=0", as_dict=1)
	
	if sale_invoices:
		for s in sale_invoices:
			 
			item_count = frappe.db.sql("select count(name) as total from `tabSales Invoice Item` where parent='{}'".format(s["parent"]), as_dict=1)
			
			if item_count:
				total_item = item_count[0]["total"]
				#get total transaction from pos invoice
				pos_invoice_count = frappe.db.sql("select count(name) as total from `tabPOS Invoice` where consolidated_invoice='{}'".format(s["parent"]), as_dict=1)
				total_pos_invoice = 1
				if pos_invoice_count and pos_invoice_count[0]["total"]>1:
						total_pos_invoice = pos_invoice_count[0]["total"]

				sql = "update `tabSales Invoice Item` set total_transaction = {} where parent='{}'".format(total_pos_invoice/total_item, s["parent"])
				 
				frappe.db.sql(sql)
	
	frappe.db.commit()
	#end update total transaction to sale invoice item
	# 				

def get_columns(filters):
	
	columns = []
	if filters.row_group == "Sale Invoice":
		columns.append({'fieldname':'row_group','label':filters.row_group,'fieldtype':'Link','options':'Sales Invoice','align':'left','width':250})
	else:
		columns.append({'fieldname':'row_group','label':filters.row_group,'fieldtype':'Data','align':'left','width':250})
	# if filters.row_group == "Product":
	# 	columns.append({"label":"Item Code","fieldname":"item_code","fieldtype":"Data","align":"left",'width':130})
	
	hide_columns = filters.get("hide_columns")
	 
	if filters.column_group !="None" and filters.row_group not in ["Date","Month","Year"]:
		 
		for c in get_dynamic_columns(filters):
			columns.append(c)

	#add total to last column

	fields = get_report_field(filters)
	for f in fields:
		if not hide_columns or  f["label"] not in hide_columns:
			columns.append({
					'fieldname':"total_" +  f['fieldname'],
					'label':"Total " + f["label"],
					'fieldtype':f['fieldtype'],
					'precision': f["precision"],
					'align':f['align']
					}
				)
	if (filters.row_group == "Sale Invoice" or filters.parent_row_group == "Sale Invoice") and filters.get("include_cancelled") == True:
		columns.append({"label":"Status","fieldname":"docstatus","fieldtype":"Data","align":"center",'width':100})
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

	fields = frappe.db.sql(sql,as_dict=1)
	 
	return fields
 
def get_conditions(filters,group_filter=None):
	conditions = ""

	start_date = filters.start_date
	end_date = filters.end_date

	conditions += " b.company =if('{0}'='None',b.company,'{0}')".format(filters.company)
	if(group_filter!=None):
		conditions += " and {} ='{}'".format(group_filter["field"],group_filter["value"].replace("'","''").replace("%","%%"))

	conditions += " AND b.posting_date between '{}' AND '{}'".format(start_date,end_date)

	if filters.get("item_group"):
		conditions += " AND a.parent_item_group in %(item_group)s"

	if filters.get("item_category"):
		conditions += " AND a.item_group in %(item_category)s"

	if filters.get("customer_group"):
		conditions += " AND b.customer_group in %(customer_group)s"

	if filters.get("price_list"):
		conditions += " AND b.selling_price_list in %(price_list)s"

	if filters.get("supplier"):
		conditions += " AND a.supplier in %(supplier)s"

	if filters.get("market_segment"):
		conditions += " AND b.market_segment in %(market_segment)s"

	if filters.get("business_source"):
		conditions += " AND b.business_source in %(business_source)s"
	if  get_accounting_dimensions():
		conditions += " AND b.department in %(department)s"
	
	if filters.get("supplier_group"):
		conditions += " AND (SELECT supplier_group FROM `tabSupplier` b WHERE b.name = a.supplier) in %(supplier_group)s"
		
	if filters.get("branch"):
		conditions += " AND b.branch in %(branch)s"

	if filters.get("pos_profile"):
		conditions += " AND b.pos_profile in %(pos_profile)s"
	
	return conditions

def get_report_data(filters,parent_row_group=None,indent=0,group_filter=None):
	
	hide_columns = filters.get("hide_columns")
	row_group = [d["fieldname"] for d in get_row_groups() if d["label"]==filters.row_group][0]
	
	if(parent_row_group!=None):
		row_group = [d["fieldname"] for d in get_row_groups() if d["label"]==parent_row_group][0]

	report_fields = get_report_field(filters)
	
	sql = "select {} as row_group, {} as indent ".format(row_group, indent)
	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
			
			sql = strip(sql)
			if sql[-1]!=",":
				sql = sql + ','
			
			for rf in report_fields:
				
				if not hide_columns or  rf["label"] not in hide_columns:
					sql = sql +	"SUM(if(b.posting_date between '{}' AND '{}',{},0)) as '{}_{}',".format(f["start_date"],f["end_date"],rf["sql_expression"],f["fieldname"],rf["fieldname"])
			#end for
	# total last column
	item_code = ""
	groupdocstatus = ""
	normal_filter = "b.docstatus in (1) AND"
	# if ((indent > 0) and ( filters.row_group == "Product" or filters.parent_row_group == "Product")):
	# 	item_code = ",a.item_code"
	
	for rf in report_fields:
		#check sql variable if last character is , then remove it
		sql = strip(sql)
		if sql[-1]==",":
			sql = sql[0:len(sql)-1]
		if not hide_columns or  rf["label"] not in hide_columns:
			sql = sql + " ,SUM({}) AS 'total_{}' ".format(rf["sql_expression"],rf["fieldname"])
	sql = sql + """ {2}
		FROM `tabSales Invoice Item` AS a
			INNER JOIN `tabSales Invoice` b on b.name = a.parent
		WHERE
			{4}
			{0}
		GROUP BY 
		{1} {2} {3}
	""".format(get_conditions(filters,group_filter), row_group,item_code,groupdocstatus,normal_filter)
	data = frappe.db.sql(sql,filters, as_dict=1)
	return data
 
def get_report_group_data(filters):
	parent = get_report_data(filters, filters.parent_row_group, 0)
	data=[] 
	for p in parent:
		p["is_group"] = 1
		data.append(p)

		row_group = [d for d in get_row_groups() if d["label"]==filters.parent_row_group][0]
		children = get_report_data(filters, None, 1, group_filter={"field":row_group["fieldname"],"value":p[row_group["parent_row_group_filter_field"]]})
		for c in children:
			data.append(c)
	return data
 
def get_report_summary(data,filters):
	hide_columns = filters.get("hide_columns")
	report_summary=[]
	if filters.parent_row_group==None:
		if not filters.is_ticket:
			report_summary =[{"label":"Total " + filters.row_group ,"value":len(data)}]
	
	fields = get_report_field(filters)

	for f in fields:
		if not hide_columns or  f["label"] not in hide_columns:
			value=sum(d["total_" + f["fieldname"]] for d in data if d["indent"]==0)
			if f["fieldtype"] == "Currency":
				value = frappe.utils.fmt_money(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), currency="USD")
				 
			elif f["fieldtype"] =="Float":
				value = "{:.2f}".format(value)
			report_summary.append({"label":"Total {}".format(f["label"]),"value":value,"indicator":f["indicator"]})	

	return report_summary

def get_report_chart(filters,data):
	columns = []
	hide_columns = filters.get("hide_columns")
	dataset = []
	colors = []

	report_fields = get_report_field(filters)

	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
			columns.append(f["label"])
		for rf in report_fields:
			if not hide_columns or  rf["label"] not in hide_columns:
				#loop sum dynamic column data data set value
				dataset_values = []
				for f in fields:
					dataset_values.append(sum(d["{}_{}".format(f["fieldname"],rf["fieldname"])] for d in data if d["indent"]==0))
					
				dataset.append({'name':rf["label"],'values':dataset_values})
				colors.append(rf["chart_color"])

	else: # if column group is none
		for d in data:
			if d["indent"] ==0:
				columns.append(d["row_group"])

		myds = []
		for rf in report_fields:
			if not hide_columns or  rf["label"] not in hide_columns:
				fieldname = 'total_'+rf["fieldname"]
				if(fieldname=="total_transaction"):
					dataset.append({'name':rf["label"],'values':(d["total_transaction"] for d in data if d["indent"]==0)})
				elif(fieldname=="total_qty"):
					dataset.append({'name':rf["label"],'values':(d["total_qty"] for d in data if d["indent"]==0)})
				elif(fieldname=="total_sub_total"):
					dataset.append({'name':rf["label"],'values':(d["total_sub_total"] for d in data if d["indent"]==0)})
				# elif(fieldname=="total_cost"):
				# 	dataset.append({'name':rf["label"],'values':(d["total_cost"] for d in data if d["indent"]==0)})
				elif(fieldname=="total_amount"):
					dataset.append({'name':rf["label"],'values':(d["total_amount"] for d in data if d["indent"]==0)})
				# elif(fieldname=="total_profit"):
				# 	dataset.append({'name':rf["label"],'values':(d["total_profit"] for d in data if d["indent"]==0)})

		 

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

	if filters.parent_row_group == "Sale Invoice" or filters.row_group == "Sale Invoice":
     
		return [
			{"label":"Quantity","short_label":"Qty", "fieldname":"qty","fieldtype":"Float","indicator":"Grey","precision":2, "align":"center","chart_color":"#FF8A65","sql_expression":"a.qty"},
			{"label":"Sub Total", "short_label":"Sub To.", "fieldname":"sub_total","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"(if(b.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate)) * a.qty"},
			#{"label":"VAT", "short_label":"VAT.", "fieldname":"tax_amount","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"a.item_tax"},		
			{"label":"Discount", "short_label":"Disc.", "fieldname":"discount_amount","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"if(a.is_foc,0,((if(b.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty)-a.net_amount)"},
   			{"label":"FOC", "short_label":"FOC", "fieldname":"foc_amount","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"if(a.is_foc,(if(b.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount,0)"},
   			{"label":"Amount", "short_label":"Amt", "fieldname":"amount","fieldtype":"Currency","indicator":"Red","precision":None, "align":"right","chart_color":"#2E7D32","sql_expression":"(a.net_amount)"},
		]
	else:
		return [
			{"label":"Transaction","short_label":"Tran.", "fieldname":"transaction","fieldtype":"Float", "indicator":"Grey","precision":2, "align":"center","chart_color":"#f030fd","sql_expression":"a.total_transaction"},
			{"label":"Quantity","short_label":"Qty", "fieldname":"qty","fieldtype":"Float","indicator":"Grey","precision":2, "align":"center","chart_color":"#FF8A65","sql_expression":"a.qty"},
			{"label":"Sub Total", "short_label":"Sub To.", "fieldname":"sub_total","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"(if(b.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate)) * a.qty"},
			#{"label":"VAT", "short_label":"VAT", "fieldname":"tax_amount","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"a.item_tax"},	
			{"label":"Discount", "short_label":"Disc.", "fieldname":"discount_amount","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"if(a.is_foc,0,((if(b.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty)-a.net_amount)"},
			{"label":"FOC", "short_label":"FOC", "fieldname":"foc_amount","fieldtype":"Currency","indicator":"Grey","precision":None, "align":"right","chart_color":"#dd5574","sql_expression":"if(a.is_foc,(if(b.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount,0)"},
   			{"label":"Amount", "short_label":"Amt", "fieldname":"amount","fieldtype":"Currency","indicator":"Red","precision":None, "align":"right","chart_color":"#2E7D32","sql_expression":"(a.net_amount)"},
		]
  
def get_row_groups():
	return [
		{
			"fieldname":"a.parent",
			"label":"Sale Invoice",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"if(coalesce(b.market_segment,'Not Set')='','Not Set',coalesce(b.market_segment,'Not Set'))",
			"label":"Market Segment",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"coalesce(b.business_source,'Not Set')",
			"label":"Market Source",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"if(coalesce(b.marketing_segment_type,'Not Set')='','Not Set',coalesce(b.marketing_segment_type,'Not Set'))",
			"label":"Market Segment Type",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"if(coalesce(b.business_source_type,'Not Set')='','Not Set',coalesce(b.business_source_type,'Not Set'))",
			"label":"Market Source Type",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"a.item_group",
			"label":"Category",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"a.parent_item_group",
			"label":"Product Group",
			"parent_row_group_filter_field":"row_group"
		},{
			"fieldname":"b.department",
			"label":"Department",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"b.company",
			"label":"Company",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"ifnull(b.branch,'Not Set')",
			"label":"Branch",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"if(ifnull(b.pos_profile,'')='','Not Set',b.pos_profile)",
			"label":"POS Profile",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"concat(ifnull(b.customer,'Not Set'),'-',b.customer_name)",
			"label":"Customer",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"b.customer_group",
			"label":"Customer Group",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"ifnull(b.Territory,'Not Set')",
			"label":"Territory",
			"parent_row_group_filter_field":"row_group"
		},
		
		{
			"fieldname":"ifnull(b.set_warehouse,'Not Set')",
			"label":"Warehouse",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"date_format(b.posting_date,'%%d/%%m/%%Y')",
			"label":"Date",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"date_format(b.posting_date,'%%m/%%Y')",
			"label":"Month",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"date_format(b.posting_date,'%%Y')",
			"label":"Year",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"ifnull(a.brand,'Not Set')",
			"label":"Brand",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"ifnull(b.membership,'Not Set')",
			"label":"Membership",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"concat(a.item_code,'-',a.item_name)",
			"label":"Product"
		},
		{
			"fieldname":"ifnull(a.supplier_name,'Not Set')",
			"label":"Supplier",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"ifnull(a.supplier_group,'Not Set')",
			"label":"Supplier Group",
			"parent_row_group_filter_field":"row_group"
		},
		{
			"fieldname":"b.selling_price_list",
			"label":"Sale Type",
			"parent_row_group_filter_field":"row_group"
		},
	]