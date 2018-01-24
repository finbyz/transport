# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days

class TruckPartsInventory(Document):
	def validate(self):
		if self.truck_part == "Battery" or self.truck_part == "Tyre":
			if not self.serial_number:
				frappe.throw(_("Please specify serial number"))
	
	def before_save(self):
		exp_life = frappe.db.get_value("Item", self.truck_part, 'lifespan')
		self.expected_life = exp_life
		
		if self.manufacturing_date:
			self.expected_end_life = add_days(self.manufacturing_date, self.expected_life)
		else:
			self.expected_end_life = add_days(self.purchase_date, self.expected_life)
			