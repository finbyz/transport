# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import formatdate

class MaintenanceLog(Document):
	def on_submit(self):
		def new_communication(self):
			url = "http://erp.agarwallogistics.net/desk#Form/Maintenance%20Log/" + self.name
			
			content = "Maintenance Log No. - <strong><a href="+url+">"+self.name+"</a></strong>, on  date: " + formatdate(self.date, "dd MMMM, YYYY") + ":-"
			content += "<p><strong>Service Parts: </strong></p><ol>"
			
			for d in self.service_detail:
				content += "<li>"
				content += "Part Name: " + d.service_item + "<br>"
				content += "Service Type: " + d.type
				content += "Expense: " + str(d.expense_amount)
				content += "</li>"
				part_content = "Maintenance Log No. - <strong><a href="+url+">"+self.name+"</a></strong>, on  date: " + formatdate(self.date, "dd MMMM, YYYY") + ":-"
				part_content += "<p>Type: " + d.type + "</p>"
				part_content += "<p>Expense: " + str(d.expense_amount) + "</p>"
				com = frappe.new_doc("Communication")
				com.subject = self.name
				com.content = part_content
				com.communication_type = "Comment"
				com.comment_type = "Comment"
				com.reference_doctype = "Truck Parts Inventory"
				com.reference_name = d.part_no
				com.user = frappe.session.user
				com.save(ignore_permissions=True)
				frappe.db.commit()
				
			content += "</ol><p>Total Service Bill: " + self.total_service_bill
			
			com = frappe.new_doc("Communication")
			com.subject = self.name
			com.content = content
			com.communication_type = "Comment"
			com.comment_type = "Comment"
			com.reference_doctype = "Truck Master"
			com.reference_name = self.truck_no
			com.user = frappe.session.user
			com.save(ignore_permissions=True)
			frappe.db.commit()
		
		for d in self.service_detail:
			if d.type == "Change":
				old_part = frappe.get_doc("Truck Parts Inventory", d.part_no)
				old_part.part_status = "Available"
				old_part.truck_no = self.truck_no
				old_part.save()
				new_part = frappe.get_doc("Truck Parts Inventory", d.new_part_no)
				new_part.part_status = "In Use"
				new_part.truck_no = self.truck_no
				new_part.save()
				frappe.db.commit()
				
		new_communication(self)
				
	def on_cancel(self):
		for d in self.service_detail:
			if d.type == "Change":
				old_part = frappe.get_doc("Truck Parts Inventory", d.part_no)
				old_part.part_status = "In Use"
				old_part.truck_no = self.truck_no
				old_part.save()
				new_part = frappe.get_doc("Truck Parts Inventory", d.new_part_no)
				new_part.part_status = "New"
				new_part.truck_no = ""
				new_part.save()
				frappe.db.commit()
