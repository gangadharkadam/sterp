cur_frm.cscript.send = function(doc, cdt, cdn) {
console.log("in tjhe sen js");
		frappe.call({
			method:"erpnext.selling.doctype.email_template.email_template.send_email",
			args: {
				notification_type:doc.raised_by,
				message:doc.reply_to_feedback				
				},
			// callback: function(r) {
				// console.log(r.message);
			// }
		});

}

$.extend(cur_frm.cscript, {
	onload: function(doc, dt, dn) {
		var usr=''
		if(doc.__islocal && user=='Administrator') {				
				frappe.call({
				method: "erpnext.support.doctype.support_ticket.support_ticket.get_admin",
				args: {
					name: cur_frm.doc.name				
				},
				callback: function(r) {
					usr=r.message;
					cur_frm.doc.raised_by=usr;
				}
				})		
		}
		else {			
				doc.raised_by=user;
		}
	}
})