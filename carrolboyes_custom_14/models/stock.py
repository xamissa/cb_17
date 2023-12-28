# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_it_wrapped = fields.Selection(string='Is it Wrapped',related='sale_id.is_it_wrapped')

    message = fields.Char(string="Sales Order Comments",related='sale_id.message')


class StockMove(models.Model):
    _inherit = "stock.move"

    user_id = fields.Many2one("res.users", string="Salesperson", related="picking_id.sale_id.user_id")

#related to Magento
# class StockQuant(models.Model):
#     _inherit = "stock.quant"

#     magento_product_count = fields.Integer(string="Product Counts", related="product_id.magento_product_count")

#     odoo_product_id = fields.Many2one(string="Odoo Product", related="product_id.magento_product_ids.odoo_product_id")

#     magento_instance_id = fields.Many2one(string="Magento Instance", related="product_id.magento_product_ids.magento_instance_id")

    

    
