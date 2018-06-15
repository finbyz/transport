frappe.listview_settings['Indent'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		return [__(doc.status), {
			"Created": "blue",
			"Completed": "green",
			"Cancelled": "red"
		}[doc.status], "status,=," + doc.status];
	}
};