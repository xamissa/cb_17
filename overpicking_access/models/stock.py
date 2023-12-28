# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError,AccessError
import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def write(self, vals):
        print("++++++++++++StockMoveStockMoveStockMove+++++++++++++",vals)
        usr =self.env.user.has_group('overpicking_access.group_over_pick')
        if 'move_line_ids' in vals:
           for val in vals['move_line_ids']:
              if val[2] and 'quantity' in val[2] and not usr:
                 if val[2]['quantity'] >self.product_uom_qty :
                     raise AccessError(_("You are not allowed to change Over Picking!"))
        return super(StockMove, self).write(vals)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self, vals):
        usr =self.env.user.has_group('overpicking_access.group_over_pick')
        if 'move_ids_without_package' in vals :
            for val in vals['move_ids_without_package']:
                if val[2] and 'quantity' in val[2]:
                   sm_line = self.env['stock.move'].browse(val[1])
                   #product_id = self.env['product.product'].browse(val[2]['product_id'])
                   """if val[2]['quantity'] > sm_line.product_id.qty_available:
                       raise UserError(_("You are not allowed to Transfer"))"""
                if val[2] and 'quantity' in val[2] and not usr:
                    line = self.env['stock.move.line'].browse(val[1])
                    print(line,line.quantity)
                    if val[2]['quantity'] >line.quantity :
                       raise exceptions.Warning(_("You are not allowed to change Over Picking"))

        if 'move_line_ids_without_package' in vals:
            for val in vals['move_line_ids_without_package']:
                print(vals)
                if val[2] and 'qty_done' in val[2]:
                   sm_line = self.env['stock.move.line'].browse(val[1])
                   #product_id = self.env['product.product'].browse(val[2]['product_id'])
                   """if val[2]['qty_done'] > sm_line.product_id.qty_available:
                       raise UserError(_("You are not allowed to Transfer"))"""
                if val[2] and 'qty_done' in val[2] and not usr:
                    line = self.env['stock.move.line'].browse(val[1])
                    print(line,line.quantity)
                    if val[2]['qty_done'] >line.quantity :
                       raise AccessError(_("You are not allowed to change  Over Picking!"))
        return super(StockPicking, self).write(vals)

  
