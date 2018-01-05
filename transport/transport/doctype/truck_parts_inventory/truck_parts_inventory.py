# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class TruckPartsInventory(Document):
	def validate(self):
		if self.truck_part == "Battery" or self.truck_part == "Tyre":
			if not self.serial_number:
				frappe.throw(_("Please specify serial number"))
