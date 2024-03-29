# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint
from frappe.utils.email_lib.receive import POP3Mailbox
from frappe.core.doctype.communication.communication import _make

def add_sales_communication(subject, content, sender, real_name, mail=None, 
	status="Open", date=None):
	lead_name = frappe.db.get_value("Lead", {"email_id": sender})
	contact_name = frappe.db.get_value("Contact", {"email_id": sender})

	if not (lead_name or contact_name):
		# none, create a new Lead
		lead = frappe.get_doc({
			"doctype":"Lead",
			"lead_name": real_name or sender,
			"email_id": sender,
			"status": status,
			"source": "Email"
		})
		lead.ignore_permissions = True
		lead.ignore_mandatory = True
		lead.insert()
		lead_name = lead.name

	parent_doctype = "Contact" if contact_name else "Lead"
	parent_name = contact_name or lead_name

	message = _make(content=content, sender=sender, subject=subject,
		doctype = parent_doctype, name = parent_name, date=date, sent_or_received="Received")
	
	if mail:
		# save attachments to parent if from mail
		doc = frappe.get_doc(parent_doctype, parent_name)
		mail.save_attachments_in_doc(doc)

class SalesMailbox(POP3Mailbox):	
	def setup(self, args=None):
		self.settings = args or frappe.get_doc("Sales Email Settings", "Sales Email Settings")
		
	def process_message(self, mail):
		if mail.from_email == self.settings.email_id:
			return
		
		add_sales_communication(mail.subject, mail.content, mail.from_email, 
			mail.from_real_name, mail=mail, date=mail.date)

def get_leads():
	if cint(frappe.db.get_value('Sales Email Settings', None, 'extract_emails')):
		SalesMailbox()

def assign_support():
	#frappe.errprint("assign suppoert tickets")
	from frappe.utils import get_url, cstr
	if get_url()=='http://smarttailor':
		check_entry = frappe.db.sql("""select name,raised_by from `tabSupport Ticket` where assign_to is null and raised_by is not null and status<>'Closed'""")
		#frappe.errprint(check_entry)
		for name,raised_by in check_entry :
			#frappe.errprint([name,raised_by])
			assign_to = frappe.db.sql("""select assign_to from `tabAssing Master` where name= %s""",raised_by)
			#frappe.errprint(assign_to[0][0])
			if assign_to :
				aa="update `tabSupport Ticket` set assign_to='"+cstr(assign_to[0][0])+"' where name = '"+name+"'"
				#frappe.errprint(aa)
				frappe.db.sql(aa)	
			else :
				aa="update `tabSupport Ticket` set assign_to='Administrator' where name = '"+name+"'"
				#frappe.errprint(aa)
				frappe.db.sql(aa)
