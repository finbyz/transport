// Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt

this.frm.add_fetch('item_code','source','source');
this.frm.add_fetch('item_code','destination','destination');
this.frm.add_fetch('item_code','truck_type','truck_type');
this.frm.add_fetch('customer','customer_code','customer_code');

cur_frm.fields_dict.item_code.get_query = function(doc) {
	return {
		"filters": [
			['Item', 'item_group', '=', "Trips"],
			['Item', 'item_name', 'like', doc.customer_code + "%"]
		]
	}
};

frappe.ui.form.on('Indent', {
	refresh: function(frm) {
		if(!frm.doc.__islocal && frm.doc.docstatus == 1 && frm.doc.status == 'Created'){
			frm.add_custom_button(__("Truck Engagement Form"), function() {
				frappe.model.open_mapped_doc({
					method : "transport.transport.doctype.indent.indent.make_truck_engagement_form",
					frm : cur_frm
				});
			}, __("Make"));
		}
	},

	item_code: function(frm){
		if(!frm.doc.item_code){
			return
		}
		frm.call({
			method: 'get_item_price',
			doc: frm.doc,
			callback: function(r){
				if(r.message.price_list_rate != 0){
					msg = "Price is available for this trip";
				} else {
					msg = "Price is not available for this trip";
				}
				frappe.msgprint(msg);
				frm.set_value('remarks', msg);
				frm.set_value('rate', r.message.price_list_rate)
			}
		})
	},

	customer: function(frm){
		frm.set_value('item_code', '');
		frm.set_value('rate', 0.0);
		frm.set_value('remarks', '');
	}
});
cur_frm.fields_dict.source.get_query = function(doc) {
	return {
		filters: {
			"customer": doc.customer
		}
	}
};

cur_frm.fields_dict.destination.get_query = function(doc) {
	return {
		filters: {
			"customer": doc.customer
		}
	}
};