import frappe
from frappe import msgprint, _, db

@frappe.whitelist()
def payment_on_submit(self, method):
	po_payments(self, method)

@frappe.whitelist()
def pi_on_submit(self, method):
	create_part_tool(self, method)

@frappe.whitelist()
def pi_on_cancel(self, method):
	cancel_part_tool(self, method)
	
def create_part_tool(self, method):
	parts = []
	url = "http://erp.agarwallogistics.net/desk#Form/Part%20Creation%20Tool/"
	for row in self.items:
		if row.item_group == "Truck Part":
			part_tool = frappe.new_doc("Part Creation Tool")
			part_tool.truck_part = row.item_code
			part_tool.part_company = row.part_company
			part_tool.number_of_parts = int(row.qty)
			part_tool.warehouse = row.part_warehouse
			part_tool.purchase_invoice = self.name
			part_tool.supplier = self.supplier
			part_tool.purchase_date = self.posting_date
			part_tool.purchase_rate = row.rate
			part_tool.save()
			frappe.db.commit()
			link = "<a href="+url+""+part_tool.name+">"+row.item_code+"</a>"
			parts.append(link)
			
	if parts:
		msgprint(_("Part Creation Tool updated for parts '%s'. Please submit the document to create parts."%(",".join(parts))))


def cancel_part_tool(self, method):
	result = frappe.db.sql("""
		SELECT 
			name as "Name"
		FROM
			`tabPart Creation Tool`
		WHERE
			purchase_invoice = '%s'"""%self.name, as_dict=True)
			
	for row in result:
		frappe.delete_doc("Part Creation Tool", row["Name"])
			
#Update PO payments on Submit
def po_payments(self, method):
	for row in self.references:
		if row.reference_doctype == "Purchase Order":
			target_po = frappe.get_doc("Purchase Order", row.reference_name)
			
			target_po.append("payments", {
				"reference_date": self.reference_date,
				"mode_of_payment": self.mode_of_payment,
				"reference_no": self.reference_no,
				"paid_amount" : row.allocated_amount,
				"payment_entry" : self.name,
				"difference_amount" : self.difference_amount
			})
		target_po.save()
		frappe.db.commit()