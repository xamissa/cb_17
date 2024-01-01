# -*- coding: utf-8 -*-

from odoo import models, fields


class CRMTeam(models.Model):
    _inherit = 'crm.team'

    route_ids = fields.Many2many('stock.route', 'crm_team_stock_location_route_rel', 'team_id', 'route_id',  string="Routes", domain=[('sale_selectable', '=', True)])
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', copy=False)
