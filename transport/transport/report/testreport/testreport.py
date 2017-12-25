# Copyright (c) 2013, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	return columns, data

	
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