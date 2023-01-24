# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.model.document import Document

class POSBackup(Document):
	def after_insert(self):
		setting = frappe.get_doc('System Settings')
		response = requests.get(setting.pos_backup_api_url)
		frappe.db.set_value('POS Backup', self.name, {
			'exception': response.json()['message'],
			'backup_url': setting.pos_backup_api_url,
			'backup_date':frappe.utils.now(),
			'backup_path':response.json()['backup_path']
		})