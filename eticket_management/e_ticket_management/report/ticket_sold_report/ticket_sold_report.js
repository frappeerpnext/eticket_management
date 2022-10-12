

frappe.query_reports["Ticket Sold Report"] = {
	"filters": [
		{
			fieldname: "start_date",
			label: "Start Date",
			fieldtype: "Date",
			default:frappe.datetime.nowdate()
		},
		{
			fieldname: "end_date",
			label: "End Date",
			fieldtype: "Date",
			default:frappe.datetime.nowdate()
		},
		{
			"fieldname": "parent_row_group",
			"label": __("Parent Row Group"),
			"fieldtype": "Select",
			"options": "None\nItem\nSale Invoice\nCashier",
			"default":"None"
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group"),
			"fieldtype": "Select",
			"options": "Item\nSale Invoice\nCashier",
			"default":"Item"
		},
		{
			"fieldname": "column_group",
			"label": __("Column Group By"),	
			"fieldtype": "Select",
			"options": "None\nDaily\nMonthly\nYearly",
			"default":"None"
		},
		{
			fieldname: "is_master_ticket",
			label: "Show Master Ticket",
			fieldtype: "Check"
		},
	]
};
