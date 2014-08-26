# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils import now, extract_email_id
import json
import requests
from frappe.utils import get_url

class SupportTicket(TransactionBase):

	def get_sender(self, comm):
		return frappe.db.get_value('Support Email Settings',None,'support_email')

	def get_subject(self, comm):
		return '[' + self.name + '] ' + (comm.subject or 'No Subject Specified')

	def get_content(self, comm):
		signature = frappe.db.get_value('Support Email Settings',None,'support_signature')
		content = comm.content
		if signature:
			content += '<p>' + signature + '</p>'
		return content

	def get_portal_page(self):
		return "ticket"

	def on_update(self):
		from frappe.utils import get_url, cstr
		frappe.errprint(get_url())
		if get_url()=='http://smarttailor':
			pass
		else:
			# self.login()
			test = {}
			support_ticket = self.get_ticket_details()
			self.call_del_keys(support_ticket)
			#test['communications'] = []
			#self.call_del_keys(support_ticket.get('communications'), test)
			self.login()
			frappe.errprint("support_ticket")
			frappe.errprint(support_ticket)
			self.tenent_based_ticket_creation(support_ticket)

	def login(self):
		login_details = {'usr': 'Administrator', 'pwd': 'admin'}
		url = 'http://smarttailor/api/method/login'
		headers = {'content-type': 'application/x-www-form-urlencoded'}
		frappe.errprint([url, 'data='+json.dumps(login_details)])
		response = requests.post(url, data='data='+json.dumps(login_details), headers=headers)

	def get_ticket_details(self):
		# return frappe.get_doc('Support Ticket', self.name)
		response = requests.get("""%(url)s/api/resource/Support Ticket/SUP-00001"""%{'url':get_url()})
		
		# frappe.errprint(["""%(url)s/api/resource/Support Ticket/%(name)s"""%{'url':get_url(), 'name':self.name}])
		return eval(response.text).get('data')

	def call_del_keys(self, support_ticket):
		if support_ticket:
			if isinstance(support_ticket, dict):
				self.del_keys(support_ticket)

			if isinstance(support_ticket, list):
				for comm in support_ticket:
					self.del_keys(comm)

	def del_keys(self, support_ticket):
		frappe.errprint(type(support_ticket))
		#del support_ticket['name']
		del support_ticket['creation']
		del support_ticket['modified']

	def tenent_based_ticket_creation(self, support_ticket):
		frappe.errprint(support_ticket)
		url = 'http://smarttailor/api/resource/Support Ticket'
		#url = 'http://192.168.5.12:7676/api/method/login'
		headers = {'content-type': 'application/x-www-form-urlencoded'}
		frappe.errprint('data='+json.dumps(support_ticket))
		response = requests.post(url, data='data='+json.dumps(support_ticket), headers=headers)

		frappe.errprint(response)
		frappe.errprint(response.text)

	def validate(self):
		self.update_status()
		self.set_lead_contact(self.raised_by)

		if self.status == "Closed":
			from frappe.widgets.form.assign_to import clear
			clear(self.doctype, self.name)

	def set_lead_contact(self, email_id):
		import email.utils
		email_id = email.utils.parseaddr(email_id)
		if email_id:
			if not self.lead:
				self.lead = frappe.db.get_value("Lead", {"email_id": email_id})
			if not self.contact:
				self.contact = frappe.db.get_value("Contact", {"email_id": email_id})

			if not self.company:
				self.company = frappe.db.get_value("Lead", self.lead, "company") or \
					frappe.db.get_default("company")

	def update_status(self):
		status = frappe.db.get_value("Support Ticket", self.name, "status")
		if self.status!="Open" and status =="Open" and not self.first_responded_on:
			self.first_responded_on = now()
		if self.status=="Closed" and status !="Closed":
			self.resolution_date = now()
		if self.status=="Open" and status !="Open":
			# if no date, it should be set as None and not a blank string "", as per mysql strict config
			self.resolution_date = None

@frappe.whitelist()
def set_status(name, status):
	st = frappe.get_doc("Support Ticket", name)
	st.status = status
	st.save()

@frappe.whitelist()
def assing_future(name, assign_in_future,raised_by,assign_to):
  	frappe.errprint("in assign")
  	from frappe.utils import get_url, cstr
	if get_url()=='http://smarttailor':
		check_entry = frappe.db.sql("""select assign_to from `tabAssing Master` where name = %s """, raised_by)
		frappe.errprint("in assign")
		if check_entry :
			frappe.errprint("chk")
			if assign_in_future=='No':
				frappe.errprint("no")
				frappe.db.sql("""delete from `tabAssing Master` where name = %s """, raised_by)	
			else :
				frappe.errprint("Yes")
				frappe.db.sql("""update `tabAssing Master` set assign_to=%s where name = %s """,(assign_to,raised_by))
		else :
			frappe.errprint("not chk")
			if assign_in_future=='Yes':
				frappe.errprint("Yes")
				am = frappe.new_doc("Assing Master")
				am.update({
				"name": raised_by,
				"assign_to": assign_to,
				"raised_by":raised_by
			})
			am.insert()

def auto_close_tickets():
	frappe.db.sql("""update `tabSupport Ticket` set status = 'Closed'
		where status = 'Replied'
		and date_sub(curdate(),interval 15 Day) > modified""")