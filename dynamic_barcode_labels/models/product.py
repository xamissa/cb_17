# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_desc = fields.Char('Barcode Description')
    is_blank_product = fields.Boolean('Is Blank product')

class Product(models.Model):
    _inherit = 'product.product'

    barcode_desc = fields.Char('Barcode Description')
