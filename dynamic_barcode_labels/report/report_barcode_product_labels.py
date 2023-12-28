# -*- coding: utf-8 -*-
from odoo import api, fields, models

class DynamicBarcodeProductLabelsParser(models.AbstractModel):
	_name = 'report.dynamic_barcode_labels.product_barcode_labels'
	_description = "Product variant barcode labels Report"

	def _get_barcode_details_info(self):
		barcode_config = \
			self.env.ref('dynamic_barcode_labels.barcode_labels_config_data')
		data = {
			'barcode_type': barcode_config.barcode_type,
			'barcode_width': barcode_config.barcode_width,
			'barcode_height': barcode_config.barcode_height,
			'barcode_currency_id': barcode_config.barcode_currency_id,
			'barcode_currency_position': barcode_config.barcode_currency_position,
		}
		return data

	@api.model
	def _get_report_values(self, docids, data=None):
		barcode_labels_report = self.env['ir.actions.report']._get_report_from_name('dynamic_barcode_labels.product_barcode_labels')
		barcode_labels = data['form']['barcode_labels']
		barcode_labels = self.env['barcode.product.labels.wiz.line'].browse(barcode_labels)
		import pdb
		pdb.set_trace()
		return {
			'doc_ids': barcode_labels,
			'doc_model': barcode_labels_report.model,
			'docs': barcode_labels,
			'data': data,
			'get_barcode_details_info': self._get_barcode_details_info(),
		}
