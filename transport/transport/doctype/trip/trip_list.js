frappe.listview_settings['Trip'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		return [__(doc.status), {
			"Not Started": "orange",
			"On Trip": "blue",
			"Completed": "green",
			"Cancelled": "red"
		}[doc.status], "status,=," + doc.status];
	}
};
