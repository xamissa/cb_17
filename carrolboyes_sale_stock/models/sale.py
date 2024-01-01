# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

from odoo import models, fields, api
class StockQuant(models.Model):
    _inherit = 'stock.quant'

    sale_id = fields.Char('Reference', copy=False)
    parent_location_id = fields.Many2one('stock.location', related='location_id.location_id', string='Parent Location', store=True)

class Saleorder(models.Model):
    _inherit = 'sale.order'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', copy=True)

    @api.onchange('team_id')
    def team_id_onchange(self):
        if self.team_id and self.team_id.analytic_account_id:
            self.analytic_account_id = self.team_id.analytic_account_id.id


class SaleorderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        res = super(SaleorderLine, self)._onchange_product_id_warning()
        if (self.product_id and self.product_id.route_ids) and (self.order_id.team_id and self.order_id.team_id.route_ids):
            route_ids = self.order_id.team_id.route_ids & self.product_id.route_ids
            self.route_id = route_ids and route_ids[0] or False
        if not self.route_id and self.order_id.warehouse_id.delivery_route_id :
               self.route_id=self.order_id.warehouse_id.delivery_route_id.id
        return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
