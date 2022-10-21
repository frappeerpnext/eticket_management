// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
/* eslint-disable */
 
frappe.query_reports["Ticket Booking Forcast"] = {
	"filters": [		
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(), 
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today()
		},
		
		{
			fieldname: "market_segment",
			label: "Market Segment",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Market Segment', txt);
			}
		},
		{
			fieldname: "business_source",
			label: "Market Source",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Lead Source', txt);
			}
		},
		{
			"fieldname": "parent_row_group",
			"label": __("Parent Group By"),
			"fieldtype": "Select",
			"options": "\nCategory\nTerritory\nDate\n\Month\nYear\nMarket Segment\nMarket Segment Type\nMarket Source\nMarket Source Type",
			
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Product\nCategory\nTerritory\nDate\n\Month\nYear\nMarket Segment\nMarket Segment Type\nMarket Source\nMarket Source Type",
			"default":"Category"
		},
		{
			"fieldname": "column_group",
			"label": __("Column Group By"),
			"fieldtype": "Select",
			"options": "Column Group By\nDaily\nWeekly\nMonthly\nQuarterly\nHalf Yearly\nYearly",
			"default":"Column Group By"
		},
		{
			"fieldname": "hide_columns",
			"label": __("Hide Columns"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"Amount","description":"Amount"},
					{"value":"Quantity","description":"Quantity"}
				]
			},
			"default":"All"
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default":"bar"
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
	
		value = default_formatter(value, row, column, data);

		if (data && data.is_group==1) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		}
		
		return value;
	},
};

 