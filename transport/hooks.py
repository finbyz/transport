# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "transport"
app_title = "Transport"
app_publisher = "FinByz Tech Pvt. Ltd."
app_description = "Managing Transport Business"
app_icon = "octicon octicon-dashboard"
app_color = "red"
app_email = "info@finbyz.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/transport/css/transport.css"
# app_include_js = "/assets/transport/js/transport.js"

# include js, css files in header of web template
# web_include_css = "/assets/transport/css/transport.css"
# web_include_js = "/assets/transport/js/transport.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "transport.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "transport.install.before_install"
# after_install = "transport.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "transport.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Payment Entry": {
		"on_submit": "transport.api.payment_on_submit",
		"on_cancel": "transport.api.payment_on_cancel"
	}
}



# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"transport.tasks.all"
# 	],
# 	"daily": [
# 		"transport.tasks.daily"
# 	],
# 	"hourly": [
# 		"transport.tasks.hourly"
# 	],
# 	"weekly": [
# 		"transport.tasks.weekly"
# 	]
# 	"monthly": [
# 		"transport.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "transport.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "transport.event.get_events"
# }

