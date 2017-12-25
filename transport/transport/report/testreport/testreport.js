// Copyright (c) 2016, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["TestReport"] = {
	"filters": [
		{
			fieldname: "truck_no",
			label: __("Truck No"),
			fieldtype: "Link",
			options: "Truck Master"
		},
		{
			fieldname: "driver",
			label: __("Driver"),
			fieldtype: "Link",
			options: "Driver Master"
		}
	]
}