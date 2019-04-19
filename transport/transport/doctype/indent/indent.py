# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.utilities.product import get_price


class Indent(Document):
	def validate(self):
		if self._action == 'submit':
			self.validate_dates()

	def validate_dates(self):
		if not self.required_by_date:
			frappe.throw(_("Please mention Required By Date."))

		if getdate(self.required_by_date) < getdate(self.date):
			frappe.throw(_("Required By Date cannot be before Date."))

	def on_submit(self):
		if not self.item_code:
			item_code = frappe.get_list("Item", filters={
					'item_group': 'Trips',
					'source': self.source,
					'destination': self.destination,
					'truck_type': self.truck_type,
				},
				fields=['name', 'source', 'destination', 'truck_type'])

			if item_code:
				self.item_code = item_code[0].name
			else:
				item = frappe.new_doc("Item")
				title = self.customer_code + '-' + self.source + '-' + self.destination + '-' + self.truck_type 
				item.item_code = title
				item.item_name = title
				item.item_group = 'Trips'
				item.stock_uom = 'MT'
				item.is_stock_item = 0
				item.source = self.source
				item.destination = self.destination
				item.truck_type = self.truck_type
				item.save()
				self.db_set('item_code', item.name)

	def on_cancel(self):
		if self.status != 'Cancelled':
			self.db_set('status', 'Cancelled')

	def before_save(self):
		if self.status != "Created":
			self.db_set('status', "Created")

	def get_item_price(self):
		price = get_price(self.item_code, "Standard Selling", "All Customer Groups", self.company)
		
		if not price:
			price = frappe._dict({'price_list_rate': 0.0})

		return price

@frappe.whitelist()
def make_truck_engagement_form(source_name, target_doc=None):
	def postprocess(source, doc):
		doc.append('indent_detail', {
			'indent': source.name,
			'item_code': source.item_code,
			'customer': source.customer,
			'source': source.source,
			'destination': source.destination,
			'truck_type': source.truck_type,
			'required_by_date': source.required_by_date
		})

	doclist = get_mapped_doc("Indent", source_name, {
			"Indent":{
				"doctype": "Truck Engagement Form",
				"field_map": {
					"posting_date": "date",
				},
				"field_no_map":{
					"naming_series"
				}
			}
	}, target_doc, postprocess)
	
	return doclist

# @frappe.whitelist()
# def make_freight_challan(source_name, target_doc=None):
# 	def postprocess(source, doc):
# 		item_name, description, stock_uom = frappe.db.get_value("Item", source.item_code, ['item_name','description', 'stock_uom'])
# 		doc.append('items',{
# 			'item_code': source.item_code,
# 			'item_name': item_name,
# 			'description': description,
# 			'uom': stock_uom,
# 			'stock_uom': stock_uom,
# 			'from': source.source,
# 			'to': source.destination,
# 			'truck_type': source.truck_type,
# 			'qty': 1.0,
# 			'schedule_date': source.required_by_date
# 		})

# 	doclist = get_mapped_doc("Indent", source_name, {
# 			"Indent":{
# 				"doctype": "Purchase Order",
# 				"field_map": {
# 					"required_by_date": "schedule_date",
# 					"name": "for_indent"
# 				},
# 				"field_no_map":{
# 					"naming_series"
# 				}
# 			}
# 	}, target_doc, postprocess)
	
# 	return doclist