# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, get_doc, throw, db
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe.model.mapper import get_mapped_doc

class TruckEngagementForm(Document):
	
	def before_save(self):
		if self.token_valid_up_to < nowdate():
			throw(_("Tax Token has expired, check and correct Truck Master"), title="Document Expired")
		if self.fitness_valid_up_to < nowdate():
			throw(_("Fitness Certificate has expired, check and correct Truck Master"), title="Document Expired")
		if self.insurance_valid_up_to < nowdate():
			throw(_("Truck Insurance has expired, check and correct Truck Master"), title="Document Expired")

	def on_submit(self):
		# Push Changes in Driver and Khalasi Contact from Truck Engagement Form status
		if self.change_dcontact:
			driver = get_doc("Driver Master", self.driver)
			driver.db_set('contact_no', self.dcontact_no)
		if self.change_kcontact:
			khalasi = get_doc("Khalasi Master", self.khalasi)
			khalasi.db_set('contact_no', self.kcontact_no)

		frappe.db.set_value("Truck Master", self.truck_no, 'status', 'Booked')
		db.commit()

@frappe.whitelist()
def make_trip(source_name, target_doc=None):
	doclist = get_mapped_doc("Truck Engagement Form", source_name, {
			"Truck Engagement Form":{
				"doctype": "Trip",
				"field_map": {
					"name": "tef"
				},
				"field_no_map":{
					"naming_series"
				}
			},
			"Indent Detail": {
				"doctype": "Indent Detail"
			}
	}, target_doc)
	
	return doclist

@frappe.whitelist()
def make_fuel_allotment(source_name, target_doc=None):
	def postprocess(source, target):
		target.paid_from = source.doctype

	doclist = get_mapped_doc("Truck Engagement Form", source_name, {
			"Truck Engagement Form":{
				"doctype": "Fuel Allotment",
				"field_map": {
					"name": "paid_for"
				},
				"field_no_map":[
					"naming_series"
				]
			}
	}, target_doc, postprocess)
	
	return doclist