# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import itertools
STANDARD_USERS = ("Guest", "Administrator")

class EmailTemplate(Document):
	pass


@frappe.whitelist()
def get_data(notification_type=None,subject=None,message=None):
	frappe.errprint(notification_type)
	customer=[]
	if notification_type =='All Customers':
		email_list=frappe.db.sql("""select admin from `tabSubAdmin Info`""",as_list=1,debug=1)
	else:
		email_list=frappe.db.sql("""select customer_email from `tabCustomer Info`""",as_list=1,debug=1)

	frappe.errprint(email_list)	
	
	from frappe.utils.user import get_user_fullname
	from frappe.utils import get_url

	sender = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
	frappe.sendmail(recipients=list(itertools.chain(*email_list)), sender=sender, subject=subject,
		message=message)		


@frappe.whitelist()
def send_email(notification_type=None,message=None):
	frappe.errprint(notification_type)
	sender = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
	frappe.sendmail(recipients=notification_type, sender=sender, subject='Feed Back',
		message=message)


