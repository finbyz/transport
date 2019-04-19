// Copyright (c) 2018, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt

let lr_list = [];

this.frm.add_fetch("indent", "customer", "customer");
this.frm.add_fetch("indent", "item_code", "item_code");
this.frm.add_fetch("indent", "source", "source");
this.frm.add_fetch("indent", "destination", "destination");

this.frm.set_query("company_address", function() {
	return {
		query: "frappe.contacts.doctype.address.address.address_query",
		filters: { link_doctype: "Company", link_name: cur_frm.doc.company} 
	};
});


this.frm.set_query("owner_address", function() {
	return {
		query: "frappe.contacts.doctype.address.address.address_query",
		filters: { link_doctype: "Supplier", link_name: cur_frm.doc.truck_owner}
	};
});

// Filter Contact based on supplier
this.frm.set_query("owner_contact", function() {
	return {
		query: "frappe.contacts.doctype.contact.contact.contact_query",
		filters: { link_doctype: "Supplier", link_name: cur_frm.doc.truck_owner}
	};
});

this.frm.fields_dict.indent_detail.grid.get_field('indent').get_query = function(doc, cdt, cdn) {
	return {
		filters: {
			"docstatus": 1,
			"status": "Created"
		}
	}
};

frappe.ui.form.on('Trip', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__("Freight Challan"), function() {
				frappe.model.open_mapped_doc({
					method : "transport.transport.doctype.trip.trip.make_freight_challan",
					frm : cur_frm
				});
			}, __("Make"));

			if(frm.doc.status == "Not Started"){
				frm.add_custom_button(__("Fuel Allotment"), function() {
					frappe.model.open_mapped_doc({
						method : "transport.transport.doctype.trip.trip.make_fuel_allotment",
						frm : cur_frm
					});
				}, __("Make"));

				var start_btn = frm.add_custom_button(__("Start"), function() {
					frm.call({
						method : 'start_button',
						doc : frm.doc,
						callback: function(r){
							if(r.message){
								frm.refresh()
							}
						}
					});
				});

				start_btn.addClass('btn-primary');
			}

			else if(frm.doc.status == "On Trip"){
				frm.add_custom_button(__("Stop"), function() {
					frm.call({
						method : 'stop_button',
						doc : frm.doc,
						callback: function(r){
							if(r.message){
								frm.refresh()
							}
						}
					});
				});
			}
		}

		if(frappe.route_options.total_fuel_qty && frappe.route_options.total_fuel_amount){
			let fuel_qty = frappe.route_options.total_fuel_qty + (frm.doc.total_fuel_qty || 0.0);
			let fuel_amount = frappe.route_options.total_fuel_amount + (frm.doc.total_fuel_amount || 0.0);
			frm.set_value('total_fuel_qty',  fuel_qty);
			frm.set_value('total_fuel_amount', fuel_amount);
			frappe.route_options = null;
			cur_frm.save_or_update();
		}
	},

	onload: function(frm){
		if(!frm.doc.__islocal){
			frm.trigger('update_lr_no');
		}
	},
	
	before_save: function(frm){
		frm.trigger('cal_total_amount');
		frm.trigger('cal_total_weight');
	},

	before_submit: function(frm){
		if (frm.doc.indent_detail.length != frm.doc.goods.length){
			if (frm.doc.indent_detail.length > frm.doc.goods.length)
				{
					frappe.msgprint("Enter associated data in the goods table");
				}
			else if (frm.doc.indent_detail.length < frm.doc.goods.length)
				{
					frappe.msgprint("Enter associated data in the indent detail table");
				}
		}
	},

	truck_owner: function(frm) {
		frappe.call({
			method:"erpnext.accounts.party.get_party_details",
			args:{
				party: frm.doc.truck_owner,
				party_type: "Supplier"
			},
			callback: function(r){
				if(r.message){
					frm.set_value('owner_contact', r.message.contact_person);
					frm.set_value('owner_address', r.message.supplier_address);
					frm.set_value('contact_display', r.message.contact_display);
					frm.set_value('contact_email', r.message.contact_email);
					frm.set_value('mobile_no', r.message.contact_mobile);
					frm.set_value('phone', r.message.contact_phone);
					frm.set_value('address_display', r.message.address_display);
				}
			}
		})
	},

	company_address: function(frm) {
		if(frm.doc.company) {
			frappe.call({
				method: "frappe.contacts.doctype.address.address.get_address_display",
				args: {"address_dict": frm.doc.company_address },
				callback: function(r) {
					if(r.message) {
						me.frm.set_value("company_address_display", r.message)
					}
				}
			})
		} else {
			frm.set_value("company_address_display", "");
		}
	},

	update_lr_no: function(frm){
		lr_list = []
		frm.doc.indent_detail.forEach(function(row){
			lr_list.push(row.lr_no)
		});
		var df = frappe.meta.get_docfield("Goods Detail","indent_no", cur_frm.doc.name);
		df.options = lr_list;
	},

	cal_total_amount: function(frm){
		let total = 0.0;
		frm.doc.goods.forEach(function(d){
			total += d.amount;
		});
		frm.set_value('total_amount', flt(total));
	},

	cal_total_weight: function(frm){
		let weight = 0.0;
		frm.doc.goods.forEach(function(d){
			weight += d.weight;
		});
		frm.set_value('total_weight', flt(weight));
	},
});

frappe.ui.form.on('Goods Detail', {
	amount: function(frm, cdt, cdn){
		frm.events.cal_total_amount(frm);
	},

	weight: function(frm, cdt, cdn){
		frm.events.cal_total_weight(frm);
	}
});

frappe.ui.form.on('Trip Indent Detail', {
	lr_no: function(frm, cdt, cdn){
		frm.events.update_lr_no(frm);

	},
	customer: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn]
		frappe.call({
			method:"erpnext.accounts.party.get_party_details",
			args:{
				"party": d.customer,
				"party_type": "Customer"
			},
			callback: function(r){
				if(r.message){
					frappe.model.set_value(cdt, cdn, 'address_display', r.message.address_display);
				}
			}
		})
	}
}); 
	
this.frm.fields_dict.truck_owner.get_query = function(doc) {
	return {
		filters: {
			"supplier_type": "Truck Owner"
		}
	}
};
