# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, now, date_diff
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_company_address

class Trip(Document):
	def on_cancel(self):
		frappe.db.set_value("Truck Engagement Form", self.tef, 'status', 'Engaged')

		for row in self.indent_detail:
			frappe.db.set_value("Indent", row.indent, 'status', 'Created')
			
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

		self.db_set('status', 'Cancelled')

	def start_button(self):
		if self.status == "Not Started":
			self.status = 'On Trip'
			self.starting_datetime = now()

			frappe.db.set_value("Truck Master", self.truck_no, 'status', 'On Trip')
			frappe.db.set_value("Driver Master", self.driver, 'status', 'On Trip')
			frappe.db.set_value("Khalasi Master", self.khalasi, 'status', 'On Trip')
			frappe.db.set_value("Truck Engagement Form", self.tef, 'status', 'On Trip')

			self.save()
		return self.status

	def stop_button(self):
		if self.status == "On Trip":
			self.status = 'Completed'
			self.ending_datetime = now()
			self.total_days = date_diff(now(), self.starting_datetime)

			frappe.db.set_value("Truck Master", self.truck_no, 'status', 'Available')
			frappe.db.set_value("Driver Master", self.driver, 'status', 'Available')
			frappe.db.set_value("Khalasi Master", self.khalasi, 'status', 'Available')
			frappe.db.set_value("Truck Engagement Form", self.tef, 'status', 'Completed')

			for row in self.indent_detail:
				frappe.db.set_value("Indent", row.indent, 'status', 'Completed')

			self.save()
		return self.status

@frappe.whitelist()
def make_fuel_allotment(source_name, target_doc=None):
	def postprocess(source, target):
		if source.freight_challan_ref and source.ownership == 'Rented':
			target.type = "Supplier"
			target.pay_to = source.supplier
		else:
			target.type = "Driver Master"
			target.pay_to = source.driver

	doclist = get_mapped_doc("Trip", source_name, {
			"Trip":{
				"doctype": "Fuel Allotment",
				"field_map": {
					"name": "paid_for",
					"doctype": "paid_from",
				},
				"field_no_map":[
					"naming_series",
					"total_amount"
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
			row.truck_no = source.truck_no
			row.truck_type = source.truck_type

	doclist = get_mapped_doc("Trip", source_name, {
			"Trip":{
				"doctype": "Purchase Order",
				"field_map": {
					"name": "for_trip"
				},
				"field_no_map":[
					"naming_series"
				]
			},
			"Trip Indent Detail": {
				"doctype": "Purchase Order Item",
				"field_map": {
					'source': 'from',
					'destination': 'to'
				}
			}
	}, target_doc, postprocess)
	
	return doclist

@frappe.whitelist()
def company_address(company):
	return get_company_address(company)
