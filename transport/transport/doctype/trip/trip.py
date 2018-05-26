# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import db
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class Trip(Document):
	def before_save(self):
		if not self.ending_datetime:
			db.set_value("Truck Master", self.truck_no, 'status', 'On Trip')
			db.set_value("Driver Master", self.driver, 'status', 'On Trip')
			db.set_value("Khalasi Master", self.khalasi, 'status', 'On Trip')

	def on_submit(self):
		if self.status == "On Trip" and self.ending_datetime:
			self.db_set('status', 'Completed')
			db.set_value("Truck Master", self.truck_no, 'status', 'Available')
			db.set_value("Driver Master", self.driver, 'status', 'Available')
			db.set_value("Khalasi Master", self.khalasi, 'status', 'Available')
			db.commit()

	def on_cancel(self):
		if self.status == "Completed":
			self.db_set('status', 'Cancelled')
			db.commit()

@frappe.whitelist()
def make_fuel_allotment(source_name, target_doc=None):
	def postprocess(source, target):
		target.paid_from = source.doctype

	doclist = get_mapped_doc("Trip", source_name, {
			"Trip":{
				"doctype": "Fuel Allotment",
				"field_map": {
					"name": "paid_for"
				},
				"field_no_map":[
					"naming_series",
					"total_amount"
				]
			}
	}, target_doc, postprocess)
	
	return doclist