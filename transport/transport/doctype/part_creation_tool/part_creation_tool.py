# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PartCreationTool(Document):
	def on_submit(self):
		for i in xrange(self.number_of_parts):
			inventory = frappe.new_doc("Truck Parts Inventory")
			inventory.creation_tool_link = self.name
			inventory.truck_part = self.truck_part
			inventory.part_company = self.part_company
			inventory.expected_life = self.expected_life
			inventory.purchase_through = "Purchase Invoice"
			inventory.ref_link = self.purchase_invoice
			inventory.purchase_date = self.purchase_date
			inventory.purchase_rate = self.purchase_rate
			inventory.supplier = self.supplier
			inventory.manufacturing_date = self.manufacturing_date
			inventory.expected_end_life = self.expected_end_life
			inventory.part_status = "New"
			inventory.title = self.truck_part
			inventory.save()
			frappe.db.commit()
			
	def on_cancel(self):
		result = frappe.db.sql("""
			SELECT 
				name as "Name", creation_tool_link as "Link"
			FROM
				`tabTruck Parts Inventory`
			WHERE
				creation_tool_link = '%s'"""%self.name, as_dict=True)
			
		for row in result:
			frappe.delete_doc("Truck Parts Inventory", row["Name"])
		