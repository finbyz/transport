# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Transport",
			"color": "red",
			"icon": "octicon octicon-dashboard",
			"type": "module",
			"label": _("Transport")
		}
	]
