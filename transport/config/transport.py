from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Master"),
			"items": [
				{
					"type": "doctype",
					"name": "Truck Master",
				},
				{
					"type": "doctype",
					"name": "Driver Master",
				},
				{
					"type": "doctype",
					"name": "Khalasi Master",
				},
			]
		},
		{
			"label": _("Trips"),
			"items": [
				{
					"type": "doctype",
					"name": "Indent"
				},
				{
					"type": "doctype",
					"name": "Truck Engagement Form"
				},
				{
					"type": "doctype",
					"name": "Trip"
				},
				{
					"type": "doctype",
					"name": "Fuel Allotment"
				},
				{
					"type": "doctype",
					"name": "Place"
				},
			]
		},
		{
			"label": _("Documents"),
			"items": [
				{
					"type": "doctype",
					"name": "Insurance Policy"
				},
				{
					"type": "doctype",
					"name": "Truck Papers"
				},

			]
		},
		{
			"label": _("Maintenance"),
			"items": [
				{
					"type": "doctype",
					"name": "Maintenance Log"
				},
				{
					"type": "doctype",
					"name": "Truck Parts Inventory",
				},
				{
					"type": "report",
					"name": "Monthly Maintenance",
					"doctype": "Maintenance Log",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Truck wise maintenance",
					"doctype": "Maintenance Log",
					"is_query_report": True
				},
				
			]
		}
	]