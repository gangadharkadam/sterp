# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils import now, extract_email_id
from frappe.model.document import Document

class FeedBack(Document):
		pass
