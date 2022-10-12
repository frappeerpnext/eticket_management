// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ticket Booking Report"] = {
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
			fieldname: "market_segment",
			label: "Market Segment",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Market Segment', txt);
			}
		},
		{
			fieldname: "marketing_segment_type",
			label: "Market Segment Type",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Marketing Segment Type', txt);
			}
		},
		{
			fieldname: "business_source",
			label: "Business Source",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Lead Source', txt);
			}
		},
		{
			fieldname: "business_source_type",
			label: "Business Source Type",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Lead Source Type', txt);
			}
		},
	]
};
