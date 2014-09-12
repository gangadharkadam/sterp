# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, validate_email_add, cint,cstr
from frappe.model.naming import make_autoname
from frappe import throw, _, msgprint
import frappe.permissions
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class EmployeeUserDisabledError(frappe.ValidationError): pass

class Employee(Document):
	def onload(self):
		self.get("__onload").salary_structure_exists = frappe.db.get_value("Salary Structure",
			{"employee": self.name, "is_active": "Yes", "docstatus": ["!=", 2]})

	def autoname(self):
		naming_method = frappe.db.get_value("HR Settings", None, "emp_created_by")
		if not naming_method:
			throw(_("Please setup Employee Naming System in Human Resource > HR Settings"))
		else:
			if naming_method=='Naming Series':
				self.name = make_autoname(self.naming_series + '.####')
			elif naming_method=='Employee Number':
				self.name = self.employee_number

		self.employee = self.name

	def validate(self):
		from erpnext.utilities import validate_status
		validate_status(self.status, ["Active", "Left"])

		self.employee = self.name
		self.validate_date()
		self.validate_email()
		self.validate_status()
		self.validate_employee_leave_approver()

		if self.user_id:
			self.validate_for_enabled_user_id()
			self.validate_duplicate_user_id()

	def on_update(self):
		if self.user_id:
			self.update_user()
			self.update_user_permissions()

		self.update_dob_event()
		self.update_leave_approver_user_permissions()

	def update_user_permissions(self):
		frappe.permissions.add_user_permission("Employee", self.name, self.user_id)
		frappe.permissions.set_user_permission_if_allowed("Company", self.company, self.user_id)

	def update_leave_approver_user_permissions(self):
		"""add employee user permission for leave approver"""
		employee_leave_approvers = [d.leave_approver for d in self.get("employee_leave_approvers")]
		if self.reports_to and self.reports_to not in employee_leave_approvers:
			employee_leave_approvers.append(frappe.db.get_value("Employee", self.reports_to, "user_id"))

		for user in employee_leave_approvers:
			frappe.permissions.add_user_permission("Employee", self.name, user)

	def update_user(self):
		# add employee role if missing
		user = frappe.get_doc("User", self.user_id)
		user.ignore_permissions = True

		if "Employee" not in user.get("user_roles"):
			user.add_roles("Employee")

		# copy details like Fullname, DOB and Image to User
		if self.employee_name and not (user.first_name and user.last_name):
			employee_name = self.employee_name.split(" ")
			if len(employee_name) >= 3:
				user.last_name = " ".join(employee_name[2:])
				user.middle_name = employee_name[1]
			elif len(employee_name) == 2:
				user.last_name = employee_name[1]

			user.first_name = employee_name[0]

		if self.date_of_birth:
			user.birth_date = self.date_of_birth

		if self.gender:
			user.gender = self.gender

		if self.image:
			if not user.user_image:
				user.user_image = self.image
				try:
					frappe.get_doc({
						"doctype": "File Data",
						"file_name": self.image,
						"attached_to_doctype": "User",
						"attached_to_name": self.user_id
					}).insert()
				except frappe.DuplicateEntryError:
					# already exists
					pass

		user.save()

	def validate_date(self):
		if self.date_of_birth and self.date_of_joining and getdate(self.date_of_birth) >= getdate(self.date_of_joining):
			throw(_("Date of Joining must be greater than Date of Birth"))

		elif self.date_of_retirement and self.date_of_joining and (getdate(self.date_of_retirement) <= getdate(self.date_of_joining)):
			throw(_("Date Of Retirement must be greater than Date of Joining"))

		elif self.relieving_date and self.date_of_joining and (getdate(self.relieving_date) <= getdate(self.date_of_joining)):
			throw(_("Relieving Date must be greater than Date of Joining"))

		elif self.contract_end_date and self.date_of_joining and (getdate(self.contract_end_date)<=getdate(self.date_of_joining)):
			throw(_("Contract End Date must be greater than Date of Joining"))

	def validate_email(self):
		if self.company_email and not validate_email_add(self.company_email):
			throw(_("Please enter valid Company Email"))
		if self.personal_email and not validate_email_add(self.personal_email):
			throw(_("Please enter valid Personal Email"))

	def validate_status(self):
		if self.status == 'Left' and not self.relieving_date:
			throw(_("Please enter relieving date."))

	def validate_for_enabled_user_id(self):
		if not self.status == 'Active':
			return
		enabled = frappe.db.sql("""select name from `tabUser` where
			name=%s and enabled=1""", self.user_id)
		if not enabled:
			throw(_("User {0} is disabled").format(self.user_id), EmployeeUserDisabledError)

	def validate_duplicate_user_id(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee` where
			user_id=%s and status='Active' and name!=%s""", (self.user_id, self.name))
		if employee:
			throw(_("User {0} is already assigned to Employee {1}").format(self.user_id, employee[0]))

	def validate_employee_leave_approver(self):
		from erpnext.hr.doctype.leave_application.leave_application import InvalidLeaveApproverError

		for l in self.get("employee_leave_approvers")[:]:
			if "Leave Approver" not in frappe.get_roles(l.leave_approver):
				self.get("employee_leave_approvers").remove(l)
				msgprint(_("{0} is not a valid Leave Approver. Removing row #{1}.").format(l.leave_approver, l.idx))

	def update_dob_event(self):
		if self.status == "Active" and self.date_of_birth \
			and not cint(frappe.db.get_value("HR Settings", None, "stop_birthday_reminders")):
			birthday_event = frappe.db.sql("""select name from `tabEvent` where repeat_on='Every Year'
				and ref_type='Employee' and ref_name=%s""", self.name)

			starts_on = self.date_of_birth + " 00:00:00"
			ends_on = self.date_of_birth + " 00:15:00"

			if birthday_event:
				event = frappe.get_doc("Event", birthday_event[0][0])
				event.starts_on = starts_on
				event.ends_on = ends_on
				event.save()
			else:
				frappe.get_doc({
					"doctype": "Event",
					"subject": _("Birthday") + ": " + self.employee_name,
					"description": _("Happy Birthday!") + " " + self.employee_name,
					"starts_on": starts_on,
					"ends_on": ends_on,
					"event_type": "Public",
					"all_day": 1,
					"send_reminder": 1,
					"repeat_this_event": 1,
					"repeat_on": "Every Year",
					"ref_type": "Employee",
					"ref_name": self.name
				}).insert()
		else:
			frappe.db.sql("""delete from `tabEvent` where repeat_on='Every Year' and
				ref_type='Employee' and ref_name=%s""", self.name)

@frappe.whitelist()
def get_retirement_date(date_of_birth=None):
	import datetime
	ret = {}
	if date_of_birth:
		dt = getdate(date_of_birth) + datetime.timedelta(21915)
		ret = {'date_of_retirement': dt.strftime('%Y-%m-%d')}
	return ret

@frappe.whitelist()
def make_salary_structure(source_name, target=None):
	target = get_mapped_doc("Employee", source_name, {
		"Employee": {
			"doctype": "Salary Structure",
			"field_map": {
				"name": "employee"
			}
		}
	})
	target.make_earn_ded_table()
	return target

def validate_employee_role(doc, method):
	# called via User hook
	if "Employee" in [d.role for d in doc.get("user_roles")]:
		if not frappe.db.get_value("Employee", {"user_id": doc.name}):
			frappe.msgprint("Please set User ID field in an Employee record to set Employee Role")
			doc.get("user_roles").remove(doc.get("user_roles", {"role": "Employee"})[0])

def validate_validity(doc, method):
	frappe.errprint("validate validity")
	from frappe.utils import get_url, cstr
	frappe.errprint(get_url())
	frappe.errprint("validate validity")
	if doc.get("__islocal") and get_url()!='http://smarttailor':
		frappe.errprint("is local and not smarttailor")
	 	res = frappe.db.sql("select name from `tabUser` where name='Administrator' and no_of_users >0")
	 	frappe.errprint(res)
	 	if  res:
	 			frappe.errprint("in res if")
	 			frappe.db.sql("update `tabUser`set no_of_users=no_of_users-1  where name='Administrator'")
				from frappe.utils import nowdate,add_months,cint
		else:
			res1 = frappe.db.sql("select count(name) from `tabUser`")
			frappe.errprint("else res1 ")
			frappe.errprint(res1)
	 		if res1 and res1[0][0]==2:
	 			frappe.errprint("else if")
	 			#frappe.db.sql("update `tabUser`set no_of_users=no_of_users-1  where name='Administrator'")
				from frappe.utils import nowdate,add_months,cint
				doc.validity_start_date=nowdate()
				doc.validity_end_date=add_months(nowdate(),1)
			else:	
	 			frappe.throw(_("Your User Creation limit is exceeded . Please contact administrator"))

	elif(get_url()!='http://smarttailor'):
		frappe.errprint("updating existing user not smarttailor")
		if doc.add_validity:
			frappe.errprint("updating existing user not smarttailor")
			res1 = frappe.db.sql("select validity from `tabUser Validity` where user_name>0 and name=%s",doc.add_validity)
			frappe.errprint(res1)
			if res1:
				frappe.errprint("else res1 ")
				frappe.errprint("update user validity")
				from frappe.utils import nowdate,add_months,cint
				doc.add_validity=''
				frappe.errprint("user validity")
				frappe.errprint(doc.add_validity)
				frappe.errprint("user validity1")
				doc.validity_start_date=nowdate()
				doc.validity_end_date=add_months(nowdate(),cint(res1[0][0]))

def update_user_permissions(doc, method):
	# called via User hook
	if "Employee" in [d.role for d in doc.get("user_roles")]:
		employee = frappe.get_doc("Employee", {"user_id": doc.name})
		employee.update_user_permissions()

def update_users(doc, method):
	#doc.add_validity=''
	from frappe.utils import get_url, cstr
	if get_url()=='http://smarttailor':
		frappe.errprint("reassigning supprot ticket to admin for disables users")
		if not doc.enabled :
			frappe.errprint(doc.name)
			abc=frappe.db.sql("""select name from `tabUser` where name=%s and enabled=0""", doc.name)
			frappe.errprint(abc)
			if abc:
				frappe.db.sql("""update `tabSupport Ticket` set assign_to='Administrator' where assign_to=%s""",doc.name)
				frappe.errprint("updated")

def create_support():
	#frappe.errprint("creating suppoert tickets")
	import requests
	import json
	pr2 = frappe.db.sql("""select site_name from `tabSubAdmin Info` """)
	for site_name in pr2:
		db_name=cstr(site_name[0]).split('.')[0]
		db_name=db_name[:16]
		abx="select name from `"+cstr(db_name)+"`.`tabSupport Ticket` where flag='false'"
		#frappe.errprint(abx)
		pr3 = frappe.db.sql(abx)
		for sn in pr3:
		 		login_details = {'usr': 'Administrator', 'pwd': 'admin'}
		 		url = 'http://smarttailor/api/method/login'
		 		headers = {'content-type': 'application/x-www-form-urlencoded'}
		 		response = requests.post(url, data='data='+json.dumps(login_details), headers=headers)
		 		test = {}
		 		url="http://"+cstr(site_name[0])+"/api/resource/Support Ticket/"+cstr(sn[0])
		 		response = requests.get(url)
				support_ticket = eval(response.text).get('data')
				del support_ticket['name']
				del support_ticket['creation']
				del support_ticket['modified']
				del support_ticket['company']
				url = 'http://smarttailor/api/resource/Support Ticket'
				headers = {'content-type': 'application/x-www-form-urlencoded'}
				response = requests.post(url, data='data='+json.dumps(support_ticket), headers=headers)
				url="http://"+cstr(site_name[0])+"/api/resource/Support Ticket/"+cstr(sn[0])
				support_ticket={}
				support_ticket['flag']='True'
				#frappe.errprint('data='+json.dumps(support_ticket))
				response = requests.put(url, data='data='+json.dumps(support_ticket), headers=headers)

def create_feedback():
	#frappe.errprint("creating feed back")
	import requests
	import json
	pr2 = frappe.db.sql("""select site_name from `tabSubAdmin Info`""")
	for site_name in pr2:
		#frappe.errprint(site_name)
		db_name=cstr(site_name[0]).split('.')[0]
		db_name=db_name[:16]
		abx="select name from `"+cstr(db_name)+"`.`tabFeed Back` where flag='false'"
		pr3 = frappe.db.sql(abx)
		for sn in pr3:
		 		login_details = {'usr': 'Administrator', 'pwd': 'admin'}
		 		url = 'http://smarttailor/api/method/login'
		 		headers = {'content-type': 'application/x-www-form-urlencoded'}
		 		response = requests.post(url, data='data='+json.dumps(login_details), headers=headers)
		 		test = {}
		 		url="http://"+cstr(site_name[0])+"/api/resource/Feed Back/"+cstr(sn[0])
		 		response = requests.get(url)
				support_ticket = eval(response.text).get('data')
				del support_ticket['name']
				del support_ticket['creation']
				del support_ticket['modified']
				url = 'http://smarttailor/api/resource/Feed Back'
				headers = {'content-type': 'application/x-www-form-urlencoded'}
				response = requests.post(url, data='data='+json.dumps(support_ticket), headers=headers)
				url="http://"+cstr(site_name[0])+"/api/resource/Feed Back/"+cstr(sn[0])
				support_ticket={}
				support_ticket['flag']='True'
				response = requests.put(url, data='data='+json.dumps(support_ticket), headers=headers)

def add_validity():
		#frappe.errprint("in add validity function")
		import requests
		import json
		from frappe.utils import nowdate, cstr,cint, flt, now, getdate, add_months
		pr1 = frappe.db.sql("""select site_name from `tabSite Master` """)
		for pr in pr1:
			if pr[0].find('.')!= -1:
				db=pr[0].split('.')[0][:16]
			else:
				db=pr[0][:16]
			qry="select validity from `"+cstr(db)+"`.`tabUser` where name='administrator' and validity>0 "
			pp1 = frappe.db.sql(qry)
			if pp1 :
				headers = {'content-type': 'application/x-www-form-urlencoded'}
				sup={'usr':'administrator','pwd':'admin'}
				url = 'http://'+pr[0]+'/api/method/login'
				response = requests.get(url, data=sup, headers=headers)
				qry1="select name from `"+cstr(db)+"`.`tabUser` where validity_end_date <CURDATE()"
				pp2 = frappe.db.sql(qry1)
				for pp in pp2:
					dt=add_months(getdate(nowdate()), cint(pp1[0][0]))
					vldt={}				
					vldt['validity_start_date']=cstr(nowdate())
					vldt['validity_end_date']=cstr(dt)
					url = 'http://'+pr[0]+'/api/resource/User/'+cstr(name)
					response = requests.put(url, data='data='+json.dumps(vldt), headers=headers)
				qry2="select name,validity_end_date from `"+cstr(db)+"`.`tabUser` where validity_end_date >=CURDATE()"
				pp3 = frappe.db.sql(qry2)
				for name,validity_end_date in pp3:
					dt=add_months(getdate(validity_end_date), cint(pp1[0][0]))
					vldt={}				
					vldt['validity_end_date']=cstr(dt)
					url = 'http://'+pr[0]+'/api/resource/User/'+cstr(name)
					response = requests.put(url, data='data='+json.dumps(vldt), headers=headers)
				vldt={}
				vldt['validity']='0'
				url = 'http://'+pr[0]+'/api/resource/User/administrator'
				response = requests.put(url, data='data='+json.dumps(vldt), headers=headers)		

def disable_user():
	#frappe.errprint("in disable user ")
	import requests
	import json
	pr2 = frappe.db.sql("""select site_name from `tabSubAdmin Info`""")
	for site_name in pr2:
		db_name=cstr(site_name[0]).split('.')[0]
		db_name=db_name[:16]
		abx="select name from `"+cstr(db_name)+"`.`tabUser` where validity_end_date<=CURDATE()"
		pr3 = frappe.db.sql(abx)
		for sn in pr3:
				headers = {'content-type': 'application/x-www-form-urlencoded'}
				sup={'usr':'administrator','pwd':'admin'}
				url = 'http://'+cstr(site_name[0])+'/api/method/login'
				response = requests.get(url, data=sup, headers=headers)
		 		url="http://"+cstr(site_name[0])+"/api/resource/User/"+cstr(sn[0])
		 		support_ticket={}
				support_ticket['enabled']=0
				response = requests.put(url, data='data='+json.dumps(support_ticket), headers=headers)