from odoo import api, fields, models, _
from odoo.exceptions import UserError,AccessError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        if self.move_type == 'in_invoice':
            if self.env.user.has_group('carrolboyes_custom_14.group_validate_bill'):
                res = super(AccountMove, self).action_post()
                return res
            else:
                raise AccessError(('You do not have permission to validate Vendor Bill!'))

        if self.env.context.get('default_move_type') == 'entry':
            if self.env.user.has_group('carrolboyes_custom_14.group_validate_bill'):
                res = super(AccountMove, self).action_post()
                return res
            else:
                raise AccessError(('You do not have permission to validate Journal Entries!'))
        return super(AccountMove, self).action_post()
