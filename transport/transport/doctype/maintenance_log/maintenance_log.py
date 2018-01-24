# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import formatdate

class MaintenanceLog(Document):
	def before_submit(self):
		for d in self.service_detail:
			if d.type == "Change from Inventory" or d.type == "Change at Garage":
				old_part = frappe.get_doc("Truck Parts Inventory", d.part_no)
				old_part.part_status = "Available"
				old_part.truck_no = ""
				old_part.warehouse = d.warehouse
				old_part.save()
				frappe.db.commit()
				if d.type == "Change from Inventory":
					if not d.new_part_no:
						frappe.throw(_("Please provide New Part No. in row %d"%d.idx))
					update_part = frappe.get_doc("Truck Parts Inventory", d.new_part_no)
					update_part.part_status = "In Use"
					update_part.truck_no = self.truck_no
					update_part.save()
					frappe.db.commit()
				else:
					if not d.serial_number:
						frappe.throw(_("Please provide serial number in row %d"%d.idx))
					elif not d.part_company:
						frappe.throw(_("Please provide part company in row %d"%d.idx))
					elif not d.purchase_rate:
						frappe.throw(_("Please provide purchase rate in row %d"%d.idx))
					elif not d.purchase_date:
						frappe.throw(_("Please provide purchase date in row %d"%d.idx))
					elif not d.new_part_link:						
						inventory = frappe.new_doc("Truck Parts Inventory")
						inventory.truck_part = d.service_item
						inventory.part_company = d.part_company
						inventory.warehouse = d.warehouse
						inventory.purchase_through = "Maintenance Log"
						inventory.ref_link = self.name
						inventory.purchase_rate = d.purchase_rate
						inventory.purchase_date = d.purchase_date
						inventory.serial_number = d.serial_number
						inventory.title = d.service_item + "-" + d.serial_number
						inventory.part_status = "In Use"
						inventory.truck_no = self.truck_no
						inventory.save()
						d.new_part_link = inventory.name
						frappe.db.commit()
						
		stock_entry = None
		for d in self.consumable_details:
			if d.from_inventory:
				if not d.warehouse:
					frappe.throw(_("Please provide warehouse in row %d of Consumable Service Table"%d.idx))
				else:
					if not stock_entry:
						stock_entry = frappe.new_doc("Stock Entry")
						stock_entry.company = self.company
						stock_entry.purpose = "Material Issue"
						stock_entry.append("items", {
							"s_warehouse": d.warehouse,
							"item_code": d.item_code,
							"qty": d.used_qty,
							"expense_account": self.expense_account,
							"cost_center": frappe.db.get_value("Company", self.company, "cost_center")
						})
					else:
						stock_entry.append("items", {
							"s_warehouse": d.warehouse,
							"item_code": d.item_code,
							"qty": d.used_qty,
							"expense_account": self.expense_account,
							"cost_center": frappe.db.get_value("Company", self.company, "cost_center")
						})
						
		if stock_entry:
			stock_entry.save()
			stock_entry.submit()
			frappe.db.commit()
			frappe.msgprint(_("New Stock Entry created."))
				
	def on_submit(self):
		def new_communication(self):
			url = "http://erp.agarwallogistics.net/desk#Form/Maintenance%20Log/" + self.name
			
			content = "Maintenance Log No. - <strong><a href="+url+">"+self.name+"</a></strong>, on  date: " + formatdate(self.date, "dd MMMM, YYYY") + ":-"
			content += "<p><strong>Service Parts: </strong></p><ol>"
			
			for d in self.service_detail:
				content += "<li>"
				content += "Part Name: " + d.service_item + "<br>"
				content += "Service Type: " + d.type + "<br>"
				content += "Service Charge: " + str(d.service_charge) + "<br>"
				
				part_content = "Maintenance Log No. - <strong><a href="+url+">"+self.name+"</a></strong>, on  date: " + formatdate(self.date, "dd MMMM, YYYY") + ":-"
				
				if d.type == "Change at Garage":
					tmp_url = "http://erp.agarwallogistics.net/desk#Form/Truck%20Parts%20Inventory/" + d.new_part_link
					content += "New Part Log: <strong><a href="+tmp_url+">"+d.new_part_link+"</a></strong>" + "<br>"
				
				
				part_content += "<p>Type: " + d.type + "</p>"
				part_content += "<p>Service Charge: " + str(d.service_charge) + "</p>"
				
				content += "</li>"
				
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
				
			content += "</ol><p>Total Service Bill: " + str(self.total_service_bill) + "</p>"
			
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
				
		new_communication(self)
				
	def on_cancel(self):
		result = frappe.db.sql("""
			SELECT 
				name as "Name", ref_link as "Link"
			FROM
				`tabTruck Parts Inventory`
			WHERE
				ref_link = '%s'"""%self.name, as_dict=True)
			
		for row in result:
			frappe.delete_doc("Truck Parts Inventory", row["Name"])
			
		for d in self.service_detail:
			if d.type == "Change from Inventory" or d.type == "Change at Garage":
				old_part = frappe.get_doc("Truck Parts Inventory", d.part_no)
				old_part.part_status = "In Use"
				old_part.truck_no = self.truck_no
				old_part.save()
				if d.type == "Change from Inventory":
					new_part = frappe.get_doc("Truck Parts Inventory", d.new_part_no)
					new_part.part_status = "New"
					new_part.truck_no = ""
					new_part.save()
				if d.type == "Change at Garage":
					d.new_part_link = ""
				frappe.db.commit()
