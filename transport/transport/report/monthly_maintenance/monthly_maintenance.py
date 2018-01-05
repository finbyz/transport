# Copyright (c) 2013, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import flt, cstr, getdate, nowdate
from erpnext.accounts.report.financial_statements import get_period_list

def execute(filters=None):
	columns, data = [], []
	if filters.get('fiscal_year'):
		company = erpnext.get_default_company()
		period_list = get_period_list(filters.get('fiscal_year'), filters.get('fiscal_year'),"Monthly", company)
		columns=get_columns()
		data=get_log_data(filters)
		chart=get_chart_data(data,period_list)
	return columns, data, None, chart

def get_columns():
	columns = [_("Log") + ":Link/Maintenance Log:100", 
				_("Truck No.") + ":Link/Truck Master:80", 
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
	fy = frappe.db.get_value('Fiscal Year', filters.get('fiscal_year'), ['year_start_date', 'year_end_date'], as_dict=True)
	
	where_clause = ''
	where_clause += filters.truck_no and " and truck_no = '%s' " % filters.truck_no or ""
	where_clause += filters.driver and " and driver = '%s'" % filters.driver or ""
	
	data = frappe.db.sql("""
		SELECT
			truck_no as "Truck No.", make as "Make", model as "Model", name as "Log", odometer as "Odometer", date as "Date", driver_name as "Driver", other_service_charge as "Other Service Charge", total_service_bill as "Total Expense"
		from
			`tabMaintenance Log`
		where
			docstatus = 1 
			and date between '%s' and '%s'
			%s
		order by date"""%(getdate(fy.year_start_date),getdate(fy.year_end_date),where_clause),as_dict=1)
		
	dl=list(data)
	
	for row in dl:
		row["Battery Expense"] = get_expense(row["Log"], "Battery", filters)
		row["Tyre Expense"] = get_expense(row["Log"], "Tyre", filters)
		row["Spares Expense"] = get_expense(row["Log"], "Spares", filters)
	return dl
	
def get_expense(log, type, filters):
	where_clause = ''
	if type == "Spares":
		where_clause += "and tr.service_item != 'Battery' and tr.service_item != 'Tyre'"
	else:
		where_clause += "and tr.service_item = '%s'" % type
	
	where_clause += filters.truck_no and "and log.truck_no = '%s' " % filters.truck_no or ""
	where_clause += log and "and tr.parent = log.name and log.name = '%s' " % log or ""
	
	return frappe.db.sql("""
		SELECT
			sum(tr.expense_amount)
		FROM
			`tabMaintenance Log` log, `tabTruck Maintenance` tr
		WHERE
			tr.docstatus = 1
			%s"""%(where_clause))[0][0] or 0		
				
def get_chart_data(data,period_list):
	battery_charge, tyre_charge, spare_charge, service_charge = [],[],[],[]
	battery_exp_data, tyre_exp_data, spare_exp_data, service_exp_data = [], [], [], []
	
	for period in period_list:
		total_battery_exp = 0
		total_tyre_exp = 0
		total_spare_exp = 0
		total_service_exp=0
		for row in data:
			if row["Date"] <= period.to_date and row["Date"] >= period.from_date:
				total_battery_exp += flt(row["Battery Expense"])
				total_tyre_exp += flt(row["Tyre Expense"])
				total_spare_exp += flt(row["Spares Expense"])
				total_service_exp += flt(row["Other Service Charge"])
				
		battery_charge.append([period.key, total_battery_exp])
		tyre_charge.append([period.key, total_tyre_exp])
		spare_charge.append([period.key, total_spare_exp])
		service_charge.append([period.key, total_service_exp])
		

	labels = [period.key.replace("_", " ").title() for period in period_list]
	
	battery_exp_data= [row[1] for row in battery_charge]
	tyre_exp_data= [row[1] for row in tyre_charge]
	spare_exp_data= [row[1] for row in spare_charge]
	service_exp_data= [row[1] for row in service_charge]
	
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