# Copyright (c) 2013, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import flt,cstr
from frappe.utils import getdate, nowdate

def execute(filters=None):
	filters.from_date = getdate(filters.from_date or nowdate())
	filters.to_date = getdate(filters.to_date or nowdate())
	columns, data = [], []
	columns=get_columns()
	data=get_log_data(filters)
	chart=get_chart_data(data, filters)

	return columns, data, None, chart

def get_columns():
	columns = [_("Truck No.") + ":Link/Truck Master:80", 
				_("Make") + ":Data:40",
				_("Model") + ":Data:100",  
				_("Odometer") + ":Int:80", 
				_("Date") + ":Date:80",  
				_("Driver") + ":Link/Driver Master:80",  
				_("Battery Expense") + ":Currency:100", 
				_("Tyre Expense") + ":Currency:90", 
				_("Spares Expense") + ":Currency:100", 
				_("Other Service Charge") + ":Currency:140",
				_("Total Expense") + ":Currency:100"
	]
	return columns

def get_log_data(filters):
	
	#where_clause = get_filter_conditions(filters)
	start_date = filters.from_date
	end_date = filters.to_date
		
	data = frappe.db.sql("""
		SELECT
			truck_no as "Truck No.", make as "Make", model as "Model", odometer as "Odometer", date as "Date", driver_name as "Driver", sum(other_service_charge) as "Other Service Charge", sum(total_service_bill) as "Total Expense"
		from
			`tabMaintenance Log`
		where
			docstatus = 1 
			and date between %s and %s
		GROUP BY
			truck_no
		ORDER BY 
			total_service_bill""", values=(start_date, end_date), as_dict=1)
		
	dl=list(data)
	
	for row in dl:
		row["Battery Expense"] = get_expense(row["Truck No."], "Battery")
		row["Tyre Expense"] = get_expense(row["Truck No."], "Tyre")
		row["Spares Expense"] = get_expense(row["Truck No."], "Spares")
	return dl
	
def get_expense(truck, type):	
	result = frappe.db.sql("""
		SELECT
			name as 'Name', truck_no as 'Truck No'
		FROM
			`tabMaintenance Log`
		WHERE
			docstatus = 1
			AND truck_no = %s""", values=(truck), as_dict=1)
			
	result = list(result)
	expense = 0.0
	for row in result:
		where_clause = ''
		where_clause += " and parent = '%s' " % row["Name"]
		if type == "Spares":
			where_clause += " and service_item != 'Battery' and service_item != 'Tyre'"
		else:
			where_clause += " and service_item = '%s'" % type
			
		expense += frappe.db.sql("""
			SELECT
				sum(expense_amount)
			FROM
				`tabTruck Maintenance`
			WHERE
				docstatus = 1 %s """%(where_clause))[0][0] or 0
				
	return expense
				
def get_chart_data(data, filters):
	#battery_charge, tyre_charge, spare_charge, service_charge = [],[],[],[]
	battery_exp_data, tyre_exp_data, spare_exp_data, service_exp_data = [], [], [], []
	
	labels = list()
	
	for row in data:
		total_battery_exp = 0
		total_tyre_exp = 0
		total_spare_exp = 0
		total_service_exp=0
		if row["Date"] <= filters.to_date and row["Date"] >= filters.from_date:
			total_battery_exp += flt(row["Battery Expense"])
			total_tyre_exp += flt(row["Tyre Expense"])
			total_spare_exp += flt(row["Spares Expense"])
			total_service_exp += flt(row["Other Service Charge"])
		
		labels.append(row["Truck No."])
		battery_exp_data.append(total_battery_exp)
		tyre_exp_data.append(total_tyre_exp)
		spare_exp_data.append(total_spare_exp)
		service_exp_data.append(total_service_exp)
		
	#labels = [row["Truck No."] for row in data]
	#battery_exp_data= [row[1] for row in battery_charge]
	#tyre_exp_data= [row[1] for row in tyre_charge]
	#spare_exp_data= [row[1] for row in spare_charge]
	#service_exp_data= [row[1] for row in service_charge]
	
	datasets = []
	if battery_exp_data:
		datasets.append({
			'title': "Battery Expense",
			'values': battery_exp_data
		})
	if tyre_exp_data:
		datasets.append({
			'title': "Tyre Expense",
			'values': tyre_exp_data
		})
	if spare_exp_data:
		datasets.append({
			'title': "Spares Expense",
			'values': spare_exp_data
		})
	if service_exp_data:
		datasets.append({
			'title': 'Other Service Charge',
			'values': service_exp_data
		})
	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}
	chart["type"] = "bar"
	return chart
	
def get_filter_conditions(filters):
	conditions = ""
	if filters.from_date:
		conditions += " and date >= %(from_date)s"
	if filters.to_date:
		conditions += " and date <= %(to_date)s"
	
	return conditions