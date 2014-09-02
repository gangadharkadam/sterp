# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
import requests
from frappe.utils import get_url
from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils import now, extract_email_id
from frappe.model.document import Document

class FeedBack(Document):

		# def validate(self):
		# 	from frappe.utils import get_url, cstr
		# 	frappe.errprint("validate")
		# 	if self.get("__islocal") and get_url()!='http://smarttailor':
		# 		frappe.errprint("local")
		# 		pr2 = frappe.db.sql("""select name from `tabFeed Back`""")
		# 		frappe.errprint("is feed back saved")
		# 		if pr2:
		# 			if frappe.session.get('user')=='Administrator':
		# 				pr1 = frappe.db.sql("""select email_id_admin from `tabUser`  where name='Administrator'""")
		# 				self.raised_by=pr1[0][0]
		# 			else:
		# 				self.raised_by=frappe.session.get('user')
		# 			frappe.errprint("cation starts")
		# 			support_ticket = self.get_ticket_details()
		# 			self.call_del_keys(support_ticket)
		# 			frappe.errprint(support_ticket)
		# 			self.login()
		# 			self.tenent_based_ticket_creation(support_ticket)

		# def login(self):
		# 	frappe.errprint("in login")
		# 	login_details = {'usr': 'Administrator', 'pwd': 'admin'}
		# 	url = 'http://smarttailor/api/method/login'
		# 	headers = {'content-type': 'application/x-www-form-urlencoded'}
		# 	frappe.errprint([url, 'data='+json.dumps(login_details)])
		# 	response = requests.post(url, data='data='+json.dumps(login_details), headers=headers)

		# def get_ticket_details(self):
		# 	frappe.errprint("in gettin details")
		# 	response = requests.get("""%(url)s/api/resource/Feed Back/FB-00001"""%{'url':get_url(), 'name':self.name})
		# 	frappe.errprint(response)
		# 	return eval(response.text).get('data')

		# def call_del_keys(self, support_ticket):
		# 	frappe.errprint("deleting del_keys")
		# 	if support_ticket:
		# 		if isinstance(support_ticket, dict):
		# 			self.del_keys(support_ticket)

		# 		if isinstance(support_ticket, list):
		# 			for comm in support_ticket:
		# 				self.del_keys(comm)

		# def del_keys(self, support_ticket):
		# 	frappe.errprint(type(support_ticket))
		# 	del support_ticket['name']
		# 	del support_ticket['creation']
		# 	del support_ticket['modified']

		# def tenent_based_ticket_creation(self, support_ticket):
		# 	frappe.errprint(support_ticket)
		# 	url = 'http://smarttailor/api/resource/Feed Back'
		# 	#url = 'http://192.168.5.12:7676/api/method/login'
		# 	headers = {'content-type': 'application/x-www-form-urlencoded'}
		# 	frappe.errprint('data='+json.dumps(support_ticket))
		# 	response = requests.post(url, data='data='+json.dumps(support_ticket), headers=headers)

		def validate(self):
			from frappe.utils import get_url, cstr
			if self.get("__islocal") and get_url()=='http://smarttailor':
				msg="Dear "+self.raised_by+"!<br><br>Thank you for your precious feedback. <br><br>We are continuously working to improve the system ,your feedback is essential for improvement of system. <br><br>Regards,  <br>Team TailorPad."
				frappe.errprint("in the send")
				frappe.errprint(self.get('customer_information'))
				from frappe.utils.user import get_user_fullname
				from frappe.utils import get_url
				#sender = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
				frappe.sendmail(recipients=self.raised_by, sender='info@tailorpad.com', subject='Thank you for Feed Back',message=msg)			
	


