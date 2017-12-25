// Copyright (c) 2016, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["test report2"] = {
		"filters": [
			{
				"fieldname": "fiscal_year",
				"label": __("Fiscal Year"),
				"fieldtype": "select",
				"options": "Fiscal Year",
				"default": frappe.defaults.get_user_default("fiscal_year"),
				"reqd": 1,
				"on_change": function(query_report) {
					var fiscal_year = query_report.get_values().fiscal_year;
					if (!fiscal_year) {
						return;
					}
					frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
						var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
						frappe.query_report_filters_by_name.from_date.set_input(fy.year_start_date);
						frappe.query_report_filters_by_name.to_date.set_input(fy.year_end_date);
						query_report.trigger_refresh();
					});
				}
			},
			{
				fieldname: "truck_no",
				label: __("Truck No"),
				fieldtype: "Link",
				options: "Truck Master"
			},
			{
				fieldname:"Service_type",
				label:__("Service Type"),
				fieldtype: "select",
				options: "Battery Expense\nTyre Expense\nSpares Expense"
			}
			
		]
	}
});	