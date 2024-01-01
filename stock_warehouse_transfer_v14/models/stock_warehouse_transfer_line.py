# -*- coding: utf-8 -*-
# Copyright© 2017 ICTSTUDIO <http://www.ictstudio.eu>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class StockWarehouseTransferLine(models.Model):
    _name = 'stock.warehouse.transfer.line'
    _rec_name = 'product_id'
    _description = 'Stock Warehouse Transfer Line'

    @api.model
    def _get_default_product_qty(self):
        return 1.0

    product_id = fields.Many2one(
            comodel_name='product.product',
            string='Product')
    product_qty = fields.Float(
            string='Quantity',
            default=_get_default_product_qty)
    product_uom_id = fields.Many2one(
            comodel_name='uom.uom',
            string='Unit of Measure')
    transfer = fields.Many2one(
            comodel_name='stock.warehouse.transfer',
            string='Transfer')
    note = fields.Text(string='Note')
    source_location = fields.Many2one(
            comodel_name='stock.location',
            string='Source Location',
            compute='_get_transfer_locations',
            store=True)
    dest_location = fields.Many2one(
            comodel_name='stock.location',
            string='Destination Location',
            compute='_get_transfer_locations',
            store=True)

    route_id = fields.Many2one(
            comodel_name="stock.route",
            string="Preferred Route")

    @api.onchange('product_id')
    def product_id_change(self):
        self.product_uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False
        if (self.product_id and self.product_id.route_ids) and (self.transfer.team_id and self.transfer.team_id.route_ids):
            route_ids = self.transfer.team_id.route_ids & self.product_id.route_ids
            self.route_id = route_ids and route_ids[0] or False

    @api.depends('transfer.source_warehouse', 'transfer.dest_warehouse')
    def _get_transfer_locations(self):
        dest_location = False
        for rec in self:
            print ('========>>',rec.transfer.source_warehouse.delivery_steps)
            if rec.transfer.source_warehouse.delivery_steps == 'pick_pack_ship':
                rec.source_location= rec.transfer.source_warehouse.wh_output_stock_loc_id.id
            elif rec.transfer.source_warehouse.delivery_steps == 'ship_only':
                rec.source_location= rec.transfer.source_location_id.id
            transit_locations = self.env['stock.location'].search(
                    [
                        ('usage', '=', 'transit')
                    ]
            )
            for location in transit_locations:
                if location.get_warehouse().id == rec.transfer.dest_warehouse.id:
                    dest_location = location.id

            if not dest_location:
                rec.dest_location = rec.transfer.dest_warehouse.transit_location.id
            else:
               rec.dest_location = rec.transfer.dest_warehouse.transit_location.id

    def get_move_vals(self, picking, group):
        self.ensure_one()
        if self.transfer.source_warehouse.delivery_steps == 'ship_only':
            return {
                'name' : self.product_id and self.product_id.name or 'Warehouse Transfer',
                'product_id' : self.product_id.id,
                'product_uom' : self.product_uom_id.id,
                'product_uom_qty' : self.product_qty,
                'location_id' : self.source_location.id,
                'location_dest_id' : self.dest_location.id,
                'picking_id' : picking.id,
                'group_id': group.id,
                'note': self.note,
                #'procure_method': 'make_to_order',
                'route_ids': [(4, self.route_id.id)] if self.route_id else []
            }
        else:
            return {
            'name' : self.product_id and self.product_id.name or 'Warehouse Transfer',
            'product_id' : self.product_id.id,
            'product_uom' : self.product_uom_id.id,
            'product_uom_qty' : self.product_qty,
            'location_id' : self.source_location.id,
            'location_dest_id' : self.dest_location.id,
            'picking_id' : picking.id,
            'group_id': group.id,
            'note': self.note,
            'procure_method': 'make_to_order',
            'route_ids': [(4, self.route_id.id)] if self.route_id else []
        }
    
    def get_move_vals2(self, picking, group):
        self.ensure_one()
        return {
            'name' : self.product_id and self.product_id.name or 'Warehouse Transfer',
            'product_id' : self.product_id.id,
            'product_uom' : self.product_uom_id.id,
            'product_uom_qty' : self.product_qty,
            'location_id' : self.transfer.dest_warehouse.transit_location.id,
            'location_dest_id' : self.transfer.dest_warehouse.lot_stock_id.id,
            'picking_id' : picking.id,
            'group_id': group.id,
            'note': self.note,
            'company_id': self.transfer.dest_warehouse.company_id.id,
        }
