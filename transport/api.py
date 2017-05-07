import frappe
from frappe import msgprint, _, db

@frappe.whitelist()
def payment_on_submit(self, method):
	po_payments(self, method)

@frappe.whitelist()
def payment_on_cancel(self, method):
	can_po_payments(self, method)



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

#CANCEL Payment
def can_po_payments(self, method):
	for row in self.references:
		if row.reference_doctype == "Purchase Order":
			existing_row_id = frappe.db.get_value("Purchase Order Payments", filters={"parent": row.reference_name, "payment_entry": self.name}, fieldname="name")
			tr = frappe.get_doc("Purchase Order Payments", existing_row_id)
			tr.parent=''
			tr.docstatus = 2
			frappe.delete_doc("Purchase Order Payments", existing_row_id)
			frappe.db.commit()


