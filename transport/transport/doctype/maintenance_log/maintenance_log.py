# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, db, throw, get_doc, new_doc, msgprint, delete_doc, get_list
from frappe.model.document import Document
from frappe.utils import formatdate, get_url_to_form, flt

class MaintenanceLog(Document):
	def before_submit(self):
		for d in self.service_detail:
			if d.type == "Change from Inventory" or d.type == "Change at Garage":
				old_part = get_doc("Truck Parts Inventory", d.part_no)
				old_part.part_status = "Available"
				old_part.truck_no = ""
				old_part.warehouse = d.warehouse
				old_part.save()

				if d.type == "Change from Inventory":
					if not d.new_part_no:
						throw(_("Please provide New Part No. in row %d"%d.idx))

					update_part = get_doc("Truck Parts Inventory", d.new_part_no)
					update_part.part_status = "In Use"
					update_part.truck_no = self.truck_no
					update_part.save()
				else:
					if not d.serial_number:
						throw(_("Please provide serial number in row %d"%d.idx))
					elif not d.part_company:
						throw(_("Please provide part company in row %d"%d.idx))
					elif not d.purchase_rate:
						throw(_("Please provide purchase rate in row %d"%d.idx))
					elif not d.purchase_date:
						throw(_("Please provide purchase date in row %d"%d.idx))
					elif not d.new_part_link:						
						inventory = new_doc("Truck Parts Inventory")
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

				db.commit()
						
		stock_entry = None
		cost_center = db.get_value("Company", self.company, "cost_center")
		for d in self.consumable_details:
			if d.from_inventory:
				if not d.warehouse:
					throw(_("Please provide warehouse in row %d of Consumable Service Table"%d.idx))
				else:
					if not stock_entry:
						stock_entry = new_doc("Stock Entry")
						stock_entry.company = self.company
						stock_entry.purpose = "Material Issue"
						stock_entry.append("items", {
							"s_warehouse": d.warehouse,
							"item_code": d.item_code,
							"qty": d.used_qty,
							"expense_account": self.expense_account,
							"cost_center": cost_center
						})
					else:
						stock_entry.append("items", {
							"s_warehouse": d.warehouse,
							"item_code": d.item_code,
							"qty": d.used_qty,
							"expense_account": self.expense_account,
							"cost_center": cost_center
						})

		if stock_entry:
			stock_entry.save()
			stock_entry.submit()
			db.commit()
			url = get_url_to_form("Stock Entry", stock_entry.name)
			idx = url.find("/desk#")
			stock_entry_url = url[:idx] + ":8081" + url[idx:]
			link = "<b><a href='{url}'>{name}</a></b>".format(url=stock_entry_url, name=stock_entry.name)
			msgprint(_("New Stock Entry {0} created!".format(link)), title="Success", indicator='green')

	def on_submit(self):

		mlog_url = get_url_to_form('Maintenance Log', self.name)
		idx = mlog_url.find("/desk#")
		mlog_link = mlog_url[:idx] + ":8081" + mlog_url[idx:]
		content = "Maintenance Log No. - <b><a href='{url}'>{name}</a></b><br>Creation Date: {date} :-<p><b>Service Parts: </b></p><ol>".format(
				url=mlog_link, 
				name=self.name, 
				date=self.get_formatted('date'))
		
		for d in self.service_detail:
			content += "<li>"
			content += "Part Name: <b>" + d.service_item + "</b><br>"
			content += "Service Type: <b>" + d.type + "</b><br>"
			content += "Service Charge: <b>" + d.get_formatted('service_charge') + "</b><br>"
			
			part_content = "Maintenance Log No. - <b><a href='{url}'>{name}</a></b><br>Creation Date: {date}:-".format(url=mlog_link.replace('localhost', 'localhost:8081'), 
				name=self.name, 
				date=self.get_formatted('date'))
			
			if d.type == "Change at Garage":
				truck_part_url = get_url_to_form("Truck Parts Inventory", d.new_part_link)
				idx = truck_part_url.find("/desk#")
				truck_part_link = truck_part_url[:idx] + ":8081" + truck_part_url[idx:]
				content += "New Part Log: <b><a href='{url}'>{name}</a></b><br>".format(url=truck_part_link, name=d.new_part_link)
				content += "New Part Rate: <b>{rate}</b><br>".format(rate=d.purchase_rate)
			
			part_content += "<p>Type: " + d.type + "</p>"
			part_content += "<p>Service Charge: " + d.get_formatted('service_charge') + "</p>"
			
			content += "</li>"
			
			com = new_doc("Communication")
			com.subject = self.name
			com.content = part_content
			com.communication_type = "Comment"
			com.comment_type = "Comment"
			com.reference_doctype = "Truck Parts Inventory"
			com.reference_name = d.part_no
			com.user = frappe.session.user
			com.save(ignore_permissions=True)
			db.commit()

		content += "</ol>"

		if self.consumable_details:
			content += "<p><b>Consumable Service: </b></p><ol>"

			for row in self.consumable_details:
				content += "<li>"
				content += "Item Code: <b>" + row.item_code + "</b><br>"
				content += "User Qty: <b>" + row.get_formatted('used_qty') + " " + row.uom + "</b><br>"

				if row.from_inventory:
					cost = flt(row.service_cost)
				else:
					cost = flt(row.amount) + flt(row.service_cost)

				content += "Cost: <b>" + str(cost) + "</b><br></li>"
			
			content += "</ol>"

		if self.other_service_charge:
			content += "<p>Other Service Charge: " + self.get_formatted('other_service_charge') + "</p>"
			
		content += "<p>Total Service Bill: " + self.get_formatted('total_service_bill') + "</p>"
		
		com = new_doc("Communication")
		com.subject = self.name
		com.content = content
		com.communication_type = "Comment"
		com.comment_type = "Comment"
		com.reference_doctype = "Truck Master"
		com.reference_name = self.truck_no
		com.user = frappe.session.user
		com.save(ignore_permissions=True)
		db.commit()

	def on_cancel(self):
		result = get_list("Truck Parts Inventory", filters={'ref_link': self.name}, fields='name')
			
		for row in result:
			delete_doc("Truck Parts Inventory", row.name)
			
		for d in self.service_detail:
			if d.type in ["Change from Inventory", "Change at Garage"]:
				old_part = get_doc("Truck Parts Inventory", d.part_no)
				old_part.part_status = "In Use"
				old_part.truck_no = self.truck_no
				old_part.save()

				if d.type == "Change from Inventory":
					new_part = get_doc("Truck Parts Inventory", d.new_part_no)
					new_part.part_status = "New"
					new_part.truck_no = ""
					new_part.save()

				if d.type == "Change at Garage":
					d.new_part_link = ""
				db.commit()
