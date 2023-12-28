# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PurchaseApproval(models.Model):
    _name = "purchase.approval"
    _description = "Purchase Approval"

    sequence = fields.Integer('Sequence')
    name = fields.Selection([
        ('create_purchase', 'Create Purchase'),
        ('validate_purchase', 'Validate Purchase'),
        ('approve_purchase', 'Approve Purchase'),
        ])
    user_ids = fields.Many2many('res.users', string='Users', required=False)
