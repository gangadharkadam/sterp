cur_frm.add_fetch('plan', 'subject', 'subject');
cur_frm.add_fetch('plan', 'message', 'message');


console.log("in the js");


cur_frm.cscript.send = function(doc, cdt, cdn) {
console.log("in tjhe sen js");
		// console.log(doc.notification_type);
		console.log(doc.subject);
		// console.log(doc.message);
		
		frappe.call({
			method:"erpnext.selling.doctype.email_template.email_template.get_data",
			args: {
				notification_type:doc.notification_type,
				subject:doc.subject,
				message:doc.message				
				},
			// callback: function(r) {
				// console.log(r.message);
			// }
		});

}

// 	cur_frm.toggle_display('master_name', doc.account_type=='Warehouse' ||
// 		in_list(['Customer', 'Supplier'], doc.master_type));
// }