# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class PartCreationTool(Document):
	
	def before_submit(self):
		if self.truck_part == "Battery" or self.truck_part == "Tyre":
			if self.number_of_parts != len(self.serial_number):
				frappe.throw(_("Please set total %d serial numbers"%self.number_of_parts))
			
		serial_list = []	
		for d in self.serial_number:
			serial = frappe.db.get_value("Truck Parts Inventory", {"serial_number": d.serial_no})
			if serial:
				frappe.throw(_("Serial number already exists for row %d!"%d.idx))
			
			if d.serial_no not in serial_list:
				serial_list.append(d.serial_no)
			else:
				frappe.throw(_("Similar serial number found in row %d"%d.idx))
	
	def on_submit(self):
		def create_part(self, serial_number=''):
			inventory = frappe.new_doc("Truck Parts Inventory")
			if self.truck_part == 'Tyre':
				inventory.type = self.type
				inventory.position = self.position
				inventory.model_name = self.model_name
			inventory.creation_tool_link = self.name
			inventory.truck_part = self.truck_part
			inventory.part_company = self.part_company
			inventory.serial_number = serial_number
			inventory.warehouse = self.warehouse
			inventory.expected_life = self.expected_life
			inventory.purchase_through = "Purchase Invoice"
			inventory.ref_link = self.purchase_invoice
			inventory.purchase_date = self.purchase_date
			inventory.purchase_rate = self.purchase_rate
			inventory.supplier = self.supplier
			inventory.manufacturing_date = self.manufacturing_date
			inventory.expected_end_life = self.expected_end_life
			inventory.part_status = "New"
			inventory.title = serial_number and (self.truck_part + "-" + serial_number) or self.truck_part
			inventory.save()
			frappe.db.commit()
			
		parts = ["Battery", "Tyre"]
		if self.truck_part in parts:
			for i in self.serial_number:
				create_part(self, i.serial_no)
		elif self.include_sr_no:
			for i in self.serial_number:
				create_part(self, i.serial_no)
			if self.number_of_parts != len(self.serial_number):
				remaining = self.number_of_parts - len(self.serial_number)
				for i in xrange(remaining):
					create_part(self)
		else:
			for i in xrange(self.number_of_parts):
				create_part(self)
		
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
		