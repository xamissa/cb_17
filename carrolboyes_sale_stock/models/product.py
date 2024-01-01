# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    partner_id =fields.Many2one('res.partner',related='picking_id.partner_id')

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    import_duties = fields.Char( string='Import Duties (%)',tracking=True,copy=False)

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    import_duties = fields.Char(related="product_tmpl_id.import_duties",string='Import Duties (%)')
