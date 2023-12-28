# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for res in self:
            prd_lst = []
            flag = False
            for line in res.order_line.filtered(lambda x: x.product_id.type == 'product'):
                quant_obj = self.env['stock.quant']
                loc_id = line.order_id.warehouse_id.lot_stock_id
                qty_available = quant_obj._get_available_quantity(line.product_id, loc_id)
                if qty_available < line.product_uom_qty:
                    prd_lst.append(line.product_id.name)
                    flag = True
        return super(SaleOrder, self).action_confirm()

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    mag_discount_amt = fields.Float(string='Discount Amount')
    discount_amt = fields.Monetary(compute='_compute_discount_amount', string='Discount Amount', readonly=True, store=True)

    @api.depends('discount')
    def _compute_discount_amount(self):
        for line in self:
            disc_amt = 0.0
            disc_amt = line.mag_discount_amt if line.mag_discount_amt else line.price_unit * (line.discount / 100.0)
            line.update({'discount_amt':disc_amt,})

# class SaleReport(models.Model):
#     _inherit= "sale.report"

#     disc_amt = fields.Float('Disc. Amt', readonly=True)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    mag_discount_amt = fields.Float(string='Discount Amount')
    discount_amt = fields.Monetary(compute='_compute_discount_amount', 
        string='Discount Amount', readonly=True, store=True)

    @api.depends('discount')
    def _compute_discount_amount(self):
        for line in self:
            disc_amt = 0.0
            disc_amt = line.mag_discount_amt if line.mag_discount_amt else line.price_unit * (line.discount / 100.0)
            line.update({'discount_amt':disc_amt,})

class AccountReport(models.Model):
    _inherit= "account.invoice.report"

    disc_amt = fields.Float('Disc. Amt', readonly=True)

    def _select(self):
        return super(AccountReport, self)._select() + ", line.discount_amt as disc_amt"