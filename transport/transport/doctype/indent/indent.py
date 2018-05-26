# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class Indent(Document):
	def before_submit(self):
		if not self.item_code:
			item_code = frappe.db.sql("""
				SELECT
					name, source, destination, truck_type
				FROM
					`tabItem`
				WHERE
					item_group = 'Trips'
					and source = '{source}'
					and destination = '{destination}'
					and truck_type = '{truck_type}' 
				""".format(
					source = self.source,
					destination = self.destination,
					truck_type = self.truck_type), as_dict=1)

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

			frappe.db.commit()

	def on_cancel(self):
		if self.status != 'Cancelled':
			self.db_set('status', 'Cancelled')
			frappe.db.commit()

@frappe.whitelist()
def make_truck_engagement_form(source_name, target_doc=None):
	def postprocess(source, doc):
		doc.append('indent_detail', {
			'indent': source.name,
			'item_code': source.item_code,
			'customer': source.customer,
			'source': source.source,
			'destination': source.destination
		})

	doclist = get_mapped_doc("Indent", source_name, {
			"Indent":{
				"doctype": "Truck Engagement Form",
				"field_map": {
					"posting_date": "date",
					"rented_truck_no": "truck_no"
				},
				"field_no_map":{
					"naming_series"
				}
			}
	}, target_doc, postprocess)
	
	return doclist

@frappe.whitelist()
def make_freight_challan(source_name, target_doc=None):
	def postprocess(source, doc):
		doc.append('items',{
				'item_code': source.item_code,
				'schedule_date': source.required_by_date
			})

	doclist = get_mapped_doc("Indent", source_name, {
			"Indent":{
				"doctype": "Purchase Order",
				"field_map": {
					"required_by_date": "schedule_date",
					"name": "for_indent"
				},
				"field_no_map":{
					"naming_series"
				}
			}
	}, target_doc, postprocess)
	
	return doclist