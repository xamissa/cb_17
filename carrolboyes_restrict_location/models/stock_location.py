# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    allowed_users = fields.Many2many(
        string="Allowed Users",
        comodel_name='res.users',
        help="""Users allowed to do operation/move from/to this location"""
             """, others users will have a popup error on transfert action""")

    @api.model
    def create(self, vals):
        if not self.user_has_groups('carrolboyes_restrict_location.location_create_access'):
            raise AccessError(_("You are not allowed to create location!"))
        else:
            return super(StockLocation, self).create(vals)
