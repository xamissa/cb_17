# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.osv import expression


class StockRoute(models.Model):
    _inherit = 'stock.route'

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        res = super()._name_search(name, domain, operator, limit, order)
        if self._context.get('team_id', False):
            team_id = self.env['crm.team'].sudo().browse(
                self._context['team_id'])
            if team_id and team_id.route_ids:
                domain = [('id', 'in', team_id.route_ids.ids)]
                args = args or []
                return self._search(expression.AND([domain, args]), limit=limit, order=order)
        return res
