frappe.listview_settings['Truck Engagement Form'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		return [__(doc.status), {
			"To Engage": "yellow",
			"Engaged": "blue",
			"On Trip": "orange",
			"Completed": "green",
			"Cancelled": "red"
		}[doc.status], "status,=," + doc.status];
	}
};
