# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_it_wrapped = fields.Selection([
        ('yes', "Yes"),
        ('no', "No")], default=False, string='Is it Wrapped')

    message = fields.Char(string="Sales Order Comments")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def onchange_product_id(self):
        product_pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id','=',self.order_id.pricelist_id.id)])
        product_ids = self.env['product.product'].search(['|',('product_tmpl_id', 'in', product_pricelist_item.product_tmpl_id.ids),('type', '=', 'service')])
        return {'domain': {'product_id': [('id', 'in', product_ids.ids)]}}
