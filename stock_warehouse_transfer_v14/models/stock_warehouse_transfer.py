# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class StockWarehouseTransfer(models.Model):
    _name = 'stock.warehouse.transfer'
    _description = 'Stock Warehouse Transfer'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'date desc, name desc'

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].sudo().next_by_code('stock.warehouse.transfer')

    @api.model
    def _get_default_date(self):
        return fields.Date.context_today(self)

    @api.model
    def _get_default_state(self):
        return 'draft'

    @api.depends('pickings.state')
    def _calc_transfer_state(self):
        for rec in self:
            if rec.pickings:
                picking_states = [p.state for p in rec.pickings]
                if 'done' in picking_states:
                    rec.state = 'done'
                else:
                    rec.state = 'picking'

            else:
                rec.state = 'draft'

    name = fields.Char(
            string='Reference',
            default=_get_default_name,copy=False)
    date = fields.Date(
            string='Date',
            default=_get_default_date)
    source_warehouse = fields.Many2one(
            comodel_name='stock.warehouse',
            string='Source Warehouse')
    dest_warehouse = fields.Many2one(
            comodel_name='stock.warehouse',
            string='Destination Warehouse')
    state = fields.Selection(
            selection=[
                ('draft', 'Draft'),
                ('picking', 'Picking'),
                ('done', 'Done'),('cancel', 'Cancelled')],
            string='Status',
            default=_get_default_state,
            store=True,
            compute=_calc_transfer_state)
    lines = fields.One2many(
            comodel_name='stock.warehouse.transfer.line',
            inverse_name='transfer',
            string='Transfer Lines')
    pickings = fields.One2many(
            comodel_name='stock.picking',
            inverse_name='transfer',
            string='Related Picking')
    company_id = fields.Many2one(
            comodel_name='res.company', string='Company', required=True,
            default=lambda self: self.env['res.company']._company_default_get(
                    'stock.warehouse.transfer'))
    route_ids = fields.Many2one(
            comodel_name="stock.route",
            string="Preferred Routes")

    team_id = fields.Many2one(
            comodel_name="crm.team",
            string="Sales Team")

    source_location_id = fields.Many2one(
            comodel_name="stock.location",
            string="Source Location")


    @api.onchange('source_warehouse')
    def auto_set_default_location(self):
        for rec in self:
            if rec.source_warehouse and rec.source_warehouse.code != 'WH':
                rec.source_location_id = rec.source_warehouse.lot_stock_id
                rec['team_id'] = False
            else:
                rec.source_location_id = False
                if rec.source_warehouse and rec.source_warehouse.code == 'WH':
                    team_id = self.env['crm.team'].search([('name','=', 'RETAIL')], limit=1)
                    if team_id:
                        rec['team_id'] = team_id.id
                else:
                    rec['team_id'] = False


    def get_transfer_picking_type(self):
        self.ensure_one()

        picking_types = self.env['stock.picking.type'].sudo().search(
                [
                    ('default_location_src_id', '=', self.source_warehouse.wh_output_stock_loc_id.id),
                    ('code', '=', 'outgoing')
                ],limit=1
        )
        if not picking_types:
           picking_types =self.source_warehouse.int_type_id
        return picking_types and picking_types

    def get_transfer_picking_type_dest(self):
        self.ensure_one()

        picking_types = self.env['stock.picking.type'].sudo().search(
                [
                    ('default_location_dest_id', '=', self.dest_warehouse.lot_stock_id.id),
                    ('code', '=', 'internal')
                ],limit=1
        )
        if not picking_types:
           picking_types =self.dest_warehouse.int_type_id
        return picking_types and picking_types

    def get_picking_vals(self):
        self.ensure_one()
        picking_type = self.get_transfer_picking_type()
        
        source_location = self.source_warehouse.wh_output_stock_loc_id.id
        if self.source_warehouse.delivery_steps == 'pick_pack_ship':
            source_location= self.source_warehouse.wh_output_stock_loc_id.id
        elif self.source_warehouse.delivery_steps == 'ship_only':
            source_location= self.source_location_id.id
        picking_vals = {
            'picking_type_id' : picking_type.id,
            'transfer' : self.id,
            'origin': self.name,
            'location_id': source_location,
            'location_dest_id':self.dest_warehouse.transit_location.id,
            'dest_warehouse': self.dest_warehouse.id
        }
        return picking_vals
    
    def get_picking_vals_second(self):
        self.ensure_one()
        picking_type = self.get_transfer_picking_type_dest()
        picking_vals = {
            'picking_type_id' : picking_type.id,
            'transfer' : self.id,
            'origin': self.name,
            'location_id':self.dest_warehouse.transit_location.id,
            'location_dest_id':self.dest_warehouse.lot_stock_id.id,
            'dest_warehouse': self.dest_warehouse.id
        }
        return picking_vals

    def action_create_picking(self):
        for rec in self:
            print(rec)
            
            if not rec.dest_warehouse.transit_location:
                  raise UserError(_('Set transit_location on Destination warehouse '))
            
            picking_vals = rec.get_picking_vals()
            picking_vals2=rec.get_picking_vals_second()
            picking = rec.pickings.sudo().create(picking_vals)
            picking2 = rec.pickings.sudo().create(picking_vals2)
            if not picking:
                _logger.error("Error Creating Picking")
                #TODO: Add  Exception

            pc_group = rec._get_procurement_group()
            for line in rec.lines:
                move_vals = line.get_move_vals(picking, pc_group)
                move_vals2 = line.get_move_vals2(picking2, pc_group)
                if move_vals:
                    move1 = self.env['stock.move'].create(move_vals)
                    move2 = self.env['stock.move'].create(move_vals2)
                    move2.move_orig_ids = [(6,0, [move1.id])]
            picking.action_confirm()
            picking.action_assign()
            picking2.action_confirm()
            picking2.action_assign()

            if pc_group:
                a_pickings = self.env['stock.picking'].sudo().search(
                        [
                            ('group_id', '=', pc_group.id)
                        ]
                )
                for pick in a_pickings:
                    pick.write({'dest_warehouse': rec.dest_warehouse.id})

    def action_view_picking(self):
        # action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')

        pickings = self.mapped('pickings')

        pc_group = self._get_procurement_group()
        if pc_group:
            pickings = self.env['stock.picking'].search(
                    [
                        ('group_id', '=', pc_group.id)
                    ]
            )

        for pick in pickings.filtered(lambda x: x.state in ('draft','waiting','confirmed')):
            pick.action_assign()
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

    @api.model
    def _prepare_procurement_group(self):
        return {'name': self.name}

    @api.model
    def _get_procurement_group(self):
        pc_groups = self.env['procurement.group'].search(
                [
                    ('name', '=', self.name)
                ]
        )
        if pc_groups:
            pc_group = pc_groups[0]
        else:
            pc_vals = self._prepare_procurement_group()
            pc_group = self.env['procurement.group'].create(pc_vals)
        return pc_group or False

    def action_cancel_picking(self):
        picking_data = self.sudo().read(['pickings'])[0]['pickings']
        for picking_id in picking_data:
            self.env['stock.picking'].browse(picking_id).action_cancel()
        states = 0
        for picking in picking_data:
            if self.env['stock.picking'].browse(picking).state == 'cancel':
                states += 1
        if len(picking_data) == states:
            self.write({'state':'cancel'})

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    button_visible = fields.Boolean('Button Visible',default=False)

    def swt_cancel(self):
        for picking_id in self:
            picking_id.action_cancel()
            swt_pick=self.search([('origin','=',picking_id.origin),('state','!=','done')])
            count = 0
            for swt in swt_pick:
                if swt.state == 'cancel':
                    count += 1
                if swt.state != 'cancel':
                    swt.action_cancel()
                    count += 1
            if count == len(swt_pick):
                swt_ref = self.env['stock.warehouse.transfer'].search([('name','=',picking_id.origin)])                        
                swt_ref.write({'state':'cancel'}) 
        return True 

    # @api.model
    # def create(self, values):
    #     if 'picking_type_id' in values and values['picking_type_id']:
    #         s = self.env['stock.picking.type'].browse(values['picking_type_id']).name
    #         values['button_visible']=True if 'Internal Transfers' in s else False
    #     return super(StockPicking, self).create(values)

    # def write(self, values):
    #     if 'picking_type_id' in values and values['picking_type_id']:
    #         s = self.env['stock.picking.type'].browse(values['picking_type_id']).name
    #         values['button_visible']=True if 'Internal Transfers' in s else False
    #     if 'picking_type_id' not in values and self.picking_type_id:
    #         s = self.picking_type_id.name
    #         values['button_visible']=True if 'Internal Transfers' in s else False
    #     return super(StockPicking, self).write(values)
