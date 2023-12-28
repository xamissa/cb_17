# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.float_utils import float_is_zero, float_compare

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_analytic_id = fields.Many2one('account.analytic.account',string='Analytic Account', copy=True,required=True)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    account_analytic_id = fields.Many2one('account.analytic.account',  copy=True,store=True, string='Analytic Account', related='order_id.account_analytic_id', readonly=False)
    
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        # tag_ids = []
        # for tag in self.analytic_tag_ids:
        #     tag_ids.append(tag.id)
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_deadline': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'analytic_account_id':self.account_analytic_id.id,
            #'tag_ids':[(6,0,tag_ids)],
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if self.product_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = diff_quantity
            res.append(template)
        return res

    @api.depends('product_id', 'date_order')
    def _compute_analytic_id_and_tag_ids(self):
        for rec in self:
            default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                product_id=rec.product_id.id,
                partner_id=rec.order_id.partner_id.id,
                user_id=rec.env.uid,
                date=rec.date_order,
                company_id=rec.company_id.id,
            )
            #rec.account_analytic_id = rec.account_analytic_id or default_analytic_account.analytic_id
            rec.account_analytic_id = rec.order_id.account_analytic_id
            rec.analytic_tag_ids = rec.analytic_tag_ids or default_analytic_account.analytic_tag_ids

