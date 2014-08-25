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
		#url='http://smarttailor/api/resource/Company'
		#import requests
		#payload = {"company_name":"shsh","abbr":"isd","default_currency":"INR"}
        #r=requests.post(url,data=payload)
                # from frappe.utils import cstr  
		# import os
		# import sys
		# import subprocess
		# import getpass
		# import logging
		# import json
		# from distutils.spawn import find_executable
		# cwd= '/home/gangadhar/workspace/smarttailor/frappe-bench/'
                # cmd='bench new-site '+self.site_name
                # self.run_commnad(cmd,cwd)
                #cmd='bench frappe --install_app erpnext '+self.site_name                
                #self.run_commnad(cmd,cwd)
                # cmd='bench frappe --install_app shopping_cart '+self.site_name                
                #self.run_commnad(cmd,cwd)
                # self.nginx_set()
                #print "setting nginx"
	        #cwd='/home/'
                #self.run_commnad('echo indictrans | sudo service nginx reload',cwd)
  
                #def run_commnad(self,cmd,cwd):
	  	#try:
		# 	subprocess.check_call(cmd, cwd=cwd, shell=True)
		# except subprocess.CalledProcessError, e:
		# 	print "Error:", e.output
		# 	raise

                #       def nginx_set(self):
                #               print "setting nginx"
                #               port='8009'                
		# nginx="""
		# server {
		# 	listen %s ;
		# 	client_max_body_size 4G;
		# 	server_name test;
		# 	keepalive_timeout 5;
		# 	sendfile on;
		# 	root /home/gangadhar/workspace/smarttailor/frappe-bench/sites;
		# 	location /private/ {
		# 		internal;
		# 		try_files /$uri =424;
		# 	}
		# 	location /assets {
		# 		try_files $uri =404;
		# 	}

		# 	location / {
		# 		try_files /test/public/$uri @magic;
		# 	}

		# 	location @magic {
		# 		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		# 		proxy_set_header Host %s;
		# 		proxy_set_header X-Use-X-Accel-Redirect True;
		# 		proxy_read_timeout 120;
		# 		proxy_redirect off;
		# 		proxy_pass  http://frappe;
		# 	}
		# }"""%(port,self.site_name)
		# with open("/home/gangadhar/workspace/smarttailor/frappe-bench/config/nginx.conf","a") as conf_file:
		# 	conf_file.write(nginx)
