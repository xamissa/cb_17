# -*- coding: utf-8 -*-

from odoo import models, fields

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    assigned_user_ids = fields.Many2many(
        "res.users", string="Assigned users",
        help="Restrict some users to only access their assigned sales team.")


    
