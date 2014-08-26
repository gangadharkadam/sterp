# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cstr
import os
import sys
import subprocess
import getpass
import logging
import json
from distutils.spawn import find_executable


class SiteMaster(Document):
	def on_update(self):
		pass
