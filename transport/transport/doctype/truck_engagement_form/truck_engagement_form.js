// Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("truck_no", "truck_owner", "truck_owner");
cur_frm.add_fetch("truck_no", "owner_contact", "owner_contact");
cur_frm.add_fetch("truck_no", "owner_address", "owner_address");
cur_frm.add_fetch("truck_no", "make", "make");
cur_frm.add_fetch("truck_no", "model", "model");
cur_frm.add_fetch("truck_no", "year_of_making", "year_of_making");
cur_frm.add_fetch("truck_no", "ownership", "ownership");
cur_frm.add_fetch("truck_no", "chassis_no", "chassis_no");
cur_frm.add_fetch("truck_no", "engine_no", "engine_no");
cur_frm.add_fetch("truck_no", "colour", "colour");
cur_frm.add_fetch("truck_no", "road_permit_no", "road_permit_no");
cur_frm.add_fetch("truck_no", "permit_valid_from", "permit_valid_from");
cur_frm.add_fetch("truck_no", "permit_valid_up_to", "permit_valid_up_to");
cur_frm.add_fetch("truck_no", "permit_states", "permit_states");
cur_frm.add_fetch("truck_no", "fitness_valid_up_to", "fitness_valid_up_to");
cur_frm.add_fetch("truck_no", "tax_token_no", "tax_token_no");
cur_frm.add_fetch("truck_no", "token_valid_from", "token_valid_from");
cur_frm.add_fetch("truck_no", "token_valid_up_to", "token_valid_up_to");
cur_frm.add_fetch("truck_no", "insurance_policy_no", "insurance_policy_no");
cur_frm.add_fetch("truck_no", "insurance_valid_up_to", "insurance_valid_up_to");
cur_frm.add_fetch("truck_no", "insurance_company", "insurance_company");

cur_frm.add_fetch("indent", "customer", "customer");
cur_frm.add_fetch("indent", "item_code", "item_code");
cur_frm.add_fetch("indent", "source", "source");
cur_frm.add_fetch("indent", "destination", "destination");

cur_frm.add_fetch("truck_owner", "tax_id", "pan_no");

cur_frm.add_fetch("owner_contact", "mobile_no", "mobile_no");
cur_frm.add_fetch("owner_contact", "phone", "phone");

cur_frm.add_fetch("driver", "person_name", "driver_name");
cur_frm.add_fetch("driver", "contact_no", "dcontact_no");
cur_frm.add_fetch("driver", "address", "daddress");
cur_frm.add_fetch("driver", "license_no", "license_no");
cur_frm.add_fetch("driver", "valid_from", "valid_from");
cur_frm.add_fetch("driver", "valid_up_to", "valid_up_to");
cur_frm.add_fetch("driver", "issued_from", "issued_from");

cur_frm.add_fetch("khalasi", "person_name", "khalasi_name");
cur_frm.add_fetch("khalasi", "contact_no", "kcontact_no");
cur_frm.add_fetch("khalasi", "address", "kaddress");

// Filter Truck Owner
this.frm.fields_dict.truck_owner.get_query = function(doc) {
	return {
		filters: {
			"supplier_type": "Truck Owner"
		}
	}
};

// Filter Truck No. based on availability and truck type
this.frm.fields_dict.truck_no.get_query = function(doc) {
	return {
		filters: {
			"status": "Available",
			"truck_type": doc.truck_type
		}
	}
};

this.frm.fields_dict.source.get_query = function(doc) {
	return {
		filters: {
			"customer": doc.customer
		}
	}
};

// Filter Item where item_group is Trips
this.frm.fields_dict.indent_detail.grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
	return {
		filters: {
			"item_group": "Trips"
		}
	}
};

// Filter Indent where status is Created and docstatus is 1
this.frm.fields_dict.indent_detail.grid.get_field('indent').get_query = function(doc, cdt, cdn) {
	return {
		filters: {
			"docstatus": 1,
			"status": "Created"
		}
	}
};

// Filter Available Drivers
this.frm.fields_dict.driver.get_query = function(doc) {
	return {
		filters: {
			"status": "Available"
		}
	}
};

// Filter Available Khalasi
this.frm.fields_dict.khalasi.get_query = function(doc) {
	return {
		filters: {
			"status": "Available"
		}
	}
};

// Filter Address based on supplier
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

frappe.ui.form.on("Truck Engagement Form", {
	// Create Mapped Document to Trip
	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			if(frm.doc.docstatus == 1 && frm.doc.status == "Engaged"){
				frm.add_custom_button(__("Trip"), function() {
					frappe.model.open_mapped_doc({
						method : "transport.transport.doctype.truck_engagement_form.truck_engagement_form.make_trip",
						frm : cur_frm
					})
				}, __("Make"));
			}

			if (frm.doc.docstatus == 0) {
				frm.add_custom_button(__("Fuel Allotment"), function() {
					frappe.model.open_mapped_doc({
						method : "transport.transport.doctype.truck_engagement_form.truck_engagement_form.make_fuel_allotment",
						frm : cur_frm
					})
				}, __("Make"));
			}

			if(!frm.doc.freight_challan_ref && frm.doc.docstatus == 0 && frm.doc.ownership == "Rented") {
				frm.add_custom_button(__("Freight Challan"), function() {
					frappe.model.open_mapped_doc({
						method : "transport.transport.doctype.truck_engagement_form.truck_engagement_form.make_freight_challan",
						frm : cur_frm
					});
				}, __("Make"));
			}
		}

		if(frappe.route_options){
			let fuel_qty = frappe.route_options.total_fuel_qty + (frm.doc.total_fuel_qty || 0.0);
			let fuel_amount = frappe.route_options.total_fuel_amount + (frm.doc.total_fuel_amount || 0.0);
			frm.set_value('total_fuel_qty',  fuel_qty);
			frm.set_value('total_fuel_amount', fuel_amount);
			frappe.route_options = null;
			frm.save();
		}
	},

	before_save: function(frm) {
		frm.set_value('status', 'To Engage');
	},

	// Set Driver contact no. read only based on change
	change_dcontact: function(frm) {
		frm.set_df_property("dcontact_no", "read_only", frm.doc.change_dcontact? 0 : 1);
	},

	// Set Khalasi contact no. read only based on change
	change_kcontact: function(frm) {
		frm.set_df_property("kcontact_no", "read_only", frm.doc.change_kcontact? 0 : 1);
	},

	//Fetch Supplier Address and Contact Details
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
	}
});
