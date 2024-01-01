# -*- coding: utf-8 -*-
from odoo import models, fields

class Stockwarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    transit_location = fields.Many2one(
            'stock.location', domain=[('usage', '=', 'transit')],
            string='Transit location')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer = fields.Many2one(
            comodel_name='stock.warehouse.transfer',
            string='Transfer')
    dest_warehouse = fields.Many2one(
            comodel_name='stock.warehouse',
            string='Destination Warehouse')
