# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

from odoo import models, fields, api, _
class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (('move_type' in vals and vals['move_type'] == 'in_invoice') or self._context.get('default_move_type')=='in_invoice' ) and  'purchase_id' in vals and vals['purchase_id']==False :
               raise UserError(_('Sorry, you are not allowed to create  vendor bill without Purchase order!!'))
        res= super(AccountMove, self).create(vals_list)
        return res
        
