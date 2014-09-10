// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.fields_dict.customer.get_query = function(doc,cdt,cdn) {
	return{	query: "erpnext.controllers.queries.customer_query" } }

frappe.provide("erpnext.support");

cur_frm.add_fetch("customer", "customer_name", "customer_name")

$.extend(cur_frm.cscript, {
	onload: function(doc, dt, dn) {
		if(in_list(user_roles,'System Manager')) {
			cur_frm.footer.help_area.innerHTML = '<p><a href="#Form/Support Email Settings/Support Email Settings">'+__("Support Email Settings")+'</a><br>\
				<span class="help">'+__("Integrate incoming support emails to Support Ticket")+'</span></p>';
		}
		var usr=''
		if(doc.__islocal && user=='Administrator') {				
				frappe.call({
				method: "erpnext.support.doctype.support_ticket.support_ticket.get_admin",
				args: {
					name: cur_frm.doc.name				
				},
				callback: function(r) {
					alert(r.message);
					usr=r.message;
					cur_frm.doc.raised_by=usr;
				}
				})		
		}
		else {			
				doc.raised_by=user;
		}
	},
	
	refresh: function(doc) {
		erpnext.toggle_naming_series();
		cur_frm.cscript.make_listing(doc);
		if(!doc.__islocal) {
			if(cur_frm.fields_dict.status.get_status()=="Write") {
				if(doc.status!='Closed') cur_frm.add_custom_button('Close Ticket', cur_frm.cscript['Close Ticket']);
				if(doc.status=='Closed') cur_frm.add_custom_button('Re-Open Ticket', cur_frm.cscript['Re-Open Ticket']);
			}
			
			cur_frm.toggle_enable(["subject", "raised_by"], false);
			cur_frm.toggle_display("description", false);
		}
		refresh_field('status');
	},
	
	make_listing: function(doc) {
		var wrapper = cur_frm.fields_dict['thread_html'].wrapper;
		
		var comm_list = frappe.get_list("Communication", {"parent": doc.name, "parenttype":"Support Ticket"})
		
		if(!comm_list.length) {
			comm_list.push({
				"sender": doc.raised_by,
				"creation": doc.creation,
				"subject": doc.subject,
				"content": doc.description});
		}
					
		cur_frm.communication_view = new frappe.views.CommunicationList({
			list: comm_list,
			parent: wrapper,
			doc: doc,
			recipients: doc.raised_by
		})

	},
		
	'Close Ticket': function() {
		cur_frm.cscript.set_status("Closed");
	},
	
	'Re-Open Ticket': function() {
		cur_frm.cscript.set_status("Open");
	},

	set_status: function(status) {
		return frappe.call({
			method: "erpnext.support.doctype.support_ticket.support_ticket.set_status",
			args: {
				name: cur_frm.doc.name,
				status: status
			},
			callback: function(r) {
				if(!r.exc) cur_frm.reload_doc();
			}
		})
		
	}
	
})

cur_frm.cscript.assign_in_future = function(){

		frappe.call({
			method: "erpnext.support.doctype.support_ticket.support_ticket.assing_future",
			args: {
				name: cur_frm.doc.name,
				assign_in_future: cur_frm.doc.assign_in_future,
				raised_by:cur_frm.doc.raised_by,
				assign_to:cur_frm.doc.assign_to
			},
			callback: function(r) {
				
			}
		})	
	
     }




