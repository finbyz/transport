# Copyright (c) 2013, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import flt,cstr
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
	columns = [_("Truck No.") + ":Link/Truck Master:100", 
				_("Make") + ":Data:50",
				_("Model") + ":Data:100",  
				_("Location") + ":data:100", 
				_("Log") + ":Link/Maintenance Log:100", 
				_("Odometer") + ":Int:80", 
				_("Date") + ":Date:100",  
				_("Driver") + ":Link/Driver Master:80",
				_("Battery Expense") + ":Currency:100", 
				_("Tyre Expense") + ":Currency:100", 
				_("Spares Expense") + ":Currency:100", 
				_("Other Service Charge") + ":Currency:120"
	]
	return columns

def get_log_data(filters):
	fy = frappe.db.get_value('Fiscal Year', filters.get('fiscal_year'), ['year_start_date', 'year_end_date'], as_dict=True)
	data = frappe.db.sql("""select
			vhcl.truck_no as "Truck No.", vhcl.make as "Make", vhcl.model as "Model",
			vhcl.location as "Location", log.name as "Log", log.odometer as "Odometer",
			log.date as "Date", log.driver as "Driver", log.other_service_charge as "Other Service Charge"
		from
			`tabTruck Master` vhcl,`tabMaintenance Log` log
		where
			vhcl.truck_no = log.truck_no and log.docstatus = 1 and log.driver = log.driver and date between %s and %s and %s
		order by date""" ,(fy.year_start_date, fy.year_end_date), as_dict=1)
	dl=list(data)
	
	#for row in dl:
	#	row["Battery Expense"] = get_expense("Battery", filters)
	#	row["Tyre Expense"] = get_expense("Tyre", filters)
	#	row["Spares Expense"] = get_expense("Spares", filters)
	#return dl
	
	for row in dl:
		row["Truck No"] = ("Truck No", filters)
		row["Model"] = ("Model", filters)
		row["Location"] = ("Location", filters)
		row["Log"] = ("Log", filters)
		row["Odometer"] = ("Odometer", filters)
		row["Date"] = ("Date", filters)
	return dl

def get_expense(type, filters):
	where_clause = ''
	if filters.truck_no:
		where_clause += "and truck_no = '%s' " % filters.truck_no
	if filters.driver:
		where_clause += "and driver = '%s' " % filters.driver
		
	result = frappe.db.sql("""
		SELECT
			name as 'Name', truck_no as 'Truck No', driver as 'Driver'
		FROM
			`tabMaintenance Log`
		WHERE
			driver = log.driver
			%s"""%(where_clause), as_dict=1)
	)
	result = list(result)
	expense = 0
	for row in result:
		where_clause = ''
		where_clause += "and parent = '%s' " % row["Name"]
		
		if type == "Driver":
			where_clause += "and driver = '%s'" type
			
		if type == "Spares":
			where_clause += "and service_item != 'Battery' and service_item != 'Tyre'"
		else:
			where_clause += "and service_item = '%s'" % type
			
		
		expense += frappe.db.sql("""
			SELECT
				sum(expense_amount)
			FROM
				`tabMaintenance Log`
			WHERE
				driver = log.driver
				%s"""%(where_clause))[0][0] or 0
				
	return expense
	
	
				
def get_chart_data(data,period_list):
	truck_no, model, location, log, odometer, date = [],[],[],[],[],[]
	battery_charge, tyre_charge, spare_charge, service_charge = [],[],[],[]
	battery_exp_data, tyre_exp_data, spare_exp_data, service_exp_data = [], [], [], []
	
	for period in period_list:
		t_truck_no = 0
		t_model = 0
		t_location = 0
		t_log = 0
		t_odometer = 0
		t_date = 0
		total_battery_exp = 0
		total_tyre_exp = 0
		total_spare_exp = 0
		total_service_exp=0
		for row in data:
			if row["Date"] <= period.to_date and row["Date"] >= period.from_date:
				t_truck_no += flt(row["truck_no"])
				t_model += flt(row["model"])
				t_location += flt(row["location"])
				t_log += flt(row["log"])
				t_odometer += flt(row["odometer"])
				t_date += flt(row["date"])
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