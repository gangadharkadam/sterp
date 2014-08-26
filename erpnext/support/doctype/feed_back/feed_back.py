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
		def on_update(self):
			# test = {}
			from frappe.utils import get_url, cstr
			frappe.errprint(get_url())
			if get_url()=='http://smarttailor':
				pass
			else:
				support_ticket = self.get_ticket_details()
				self.call_del_keys(support_ticket)
				frappe.errprint(support_ticket)
				self.login()
				self.tenent_based_ticket_creation(support_ticket)

		def login(self):
			login_details = {'usr': 'Administrator', 'pwd': 'admin'}
			url = 'http://smarttailor/api/method/login'
			headers = {'content-type': 'application/x-www-form-urlencoded'}
			frappe.errprint([url, 'data='+json.dumps(login_details)])
			response = requests.post(url, data='data='+json.dumps(login_details), headers=headers)

		def get_ticket_details(self):
			# return frappe.get_doc('Support Ticket', self.name)
			response = requests.get("""%(url)s/api/resource/Feed Back/FB-00002"""%{'url':get_url(), 'name':self.name})
			
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
			del support_ticket['name']
			del support_ticket['creation']
			del support_ticket['modified']

		def tenent_based_ticket_creation(self, support_ticket):
			frappe.errprint(support_ticket)
			url = 'http://smarttailor/api/resource/Feed Back'
			#url = 'http://192.168.5.12:7676/api/method/login'
			headers = {'content-type': 'application/x-www-form-urlencoded'}
			frappe.errprint('data='+json.dumps(support_ticket))
			response = requests.post(url, data='data='+json.dumps(support_ticket), headers=headers)
	


