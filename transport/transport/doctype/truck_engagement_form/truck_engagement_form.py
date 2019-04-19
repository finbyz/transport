# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate
from frappe.model.mapper import get_mapped_doc

class TruckEngagementForm(Document):
	def validate(self):
		if self._action == 'submit':
			self.validate_truck_details()

		if self.token_valid_up_to < nowdate():
			frappe.msgprint(_("Tax Token has expired, check and correct Truck Master"), title="Document Expired")
		if self.fitness_valid_up_to < nowdate():
			frappe.msgprint(_("Fitness Certificate has expired, check and correct Truck Master"), title="Document Expired")
		if self.insurance_valid_up_to < nowdate():
			frappe.msgprint(_("Truck Insurance has expired, check and correct Truck Master"), title="Document Expired")
		if self.valid_up_to < nowdate():
			frappe.msgprint(_("Driver License has expired, check and correct Driver Master"), title="License Expired")

	def validate_truck_details(self):
		if not self.truck_no:
			frappe.throw(_("Please set Truck no"))

		status = frappe.db.get_value("Truck Master", self.truck_no, 'status')

		if status != "Available":
			frappe.throw(_("Current Truck is already {}. Please select another Truck.".format(status)))

		status = frappe.db.get_value("Driver Master", self.driver, 'status')

		if status != "Available":
			frappe.throw(_("Current Driver is already {}. Please select another Driver.".format(status)))

		if self.khalasi:
			status = frappe.db.get_value("Khalasi Master", self.khalasi, 'status')

			if status != "Available":
				frappe.throw(_("Current Khalasi is already {}. Please select another Khalasi.".format(status)))


	def on_submit(self):
		frappe.db.set_value("Driver Master", self.driver, 'status', 'Booked')
		
		if self.change_dcontact:
			frappe.db.set_value("Driver Master", self.driver, 'contact_no', self.dcontact_no)

		if self.khalasi:
			frappe.db.set_value("Khalasi Master", self.khalasi, 'status', 'Booked')
			if self.change_kcontact:
				frappe.db.set_value("Khalasi Master", self.khalasi, 'contact_no', self.kcontact_no)

		frappe.db.set_value("Truck Master", self.truck_no, 'status', 'Booked')
		self.status = 'Engaged'
		self.save()

	def on_cancel(self):
		fuel_allotments = frappe.get_list("Fuel Allotment", 
			filters={
				'docstatus': 1,
				'paid_from': self.doctype, 
				'paid_for': self.name,
			})

		for fuels in fuel_allotments:
			fuel = frappe.get_doc("Fuel Allotment", fuels)
			self.db_set('total_fuel_qty', self.total_fuel_qty - fuel.total_qty)
			self.db_set('total_fuel_amount', self.total_fuel_amount - fuel.total_amount)
			fuel.cancel()

		frappe.db.set_value("Driver Master", self.driver, 'status', 'Available')

		if self.khalasi:
			frappe.db.set_value("Khalasi Master", self.khalasi, 'status', 'Available')

		frappe.db.set_value("Truck Master", self.truck_no, 'status', 'Available')
		self.db_set('status', 'Cancelled')

	def get_indents(self):
		if not self.required_by_date:
			frappe.throw("Please set Required By Date!")
			return

		condition = ''
		condition += self.required_by_date and " and required_by_date <= '%s'" % self.required_by_date or ''
		condition += self.customer and " and customer = '%s'" % frappe.db.escape(self.customer) or ''
		condition += self.source and " and source = '%s'" % frappe.db.escape(self.source) or ''
		
		data = frappe.db.sql("""
			SELECT
				name, customer, item_code, source, destination, required_by_date
			FROM
				`tabIndent`
			WHERE
				docstatus = 1
				and status = 'Created' {condition} 
			ORDER BY
				required_by_date """.format(condition = condition), as_dict=1)

		if data:
			for row in data:
				self.append('indent_detail', {
					'indent': row.name,
					'customer': row.customer,
					'required_by_date': row.required_by_date,
					'item_code':row.item_code,
					'source': row.source,
					'destination':row.destination
				})

@frappe.whitelist()
def make_trip(source_name, target_doc=None):
	doclist = get_mapped_doc("Truck Engagement Form", source_name, {
			"Truck Engagement Form":{
				"doctype": "Trip",
				"field_map": {
					"name": "tef"
				},
				"field_no_map":{
					"naming_series",
					"status",
				}
			},
			"Indent Detail": {
				"doctype": "Trip Indent Detail"
			}
	}, target_doc)
	
	return doclist

@frappe.whitelist()
def make_fuel_allotment(source_name, target_doc=None):
	def postprocess(source, target):
		if source.freight_challan_ref and source.ownership == 'Rented':
			target.type = "Supplier"
			target.pay_to = source.supplier
		else:
			target.type = "Driver Master"
			target.pay_to = source.driver

	doclist = get_mapped_doc("Truck Engagement Form", source_name, {
			"Truck Engagement Form":{
				"doctype": "Fuel Allotment",
				"field_map": {
					"name": "paid_for",
					"doctype": "paid_from",
				},
				"field_no_map":[
					"naming_series"
				]
			}
	}, target_doc, postprocess)
	
	return doclist

@frappe.whitelist()
def make_freight_challan(source_name, target_doc=None):
	def postprocess(source, doc):
		for row in doc.items:
			item_name, description, stock_uom = frappe.db.get_value("Item", row.item_code, ['item_name','description', 'stock_uom'])
			row.item_name = item_name
			row.description = description
			row.uom = row.stock_uom = stock_uom
			row.qty = 1.0
			row.schedule_date = source.required_by_date

	doclist = get_mapped_doc("Truck Engagement Form", source_name, {
			"Truck Engagement Form":{
				"doctype": "Purchase Order",
				"field_map": {
					"required_by_date": "schedule_date",
					"name": "for_tef",
					"truck_owner": "supplier",
				},
				"field_no_map":[
					"naming_series"
				]
			},
			"Indent Detail": {
				"doctype": "Purchase Order Item",
				"field_map": {
					'source': 'from',
					'destination': 'to'
				}
			}
	}, target_doc, postprocess)
	
	return doclist
