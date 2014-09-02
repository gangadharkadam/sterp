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