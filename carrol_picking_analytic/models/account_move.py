from odoo import api, fields, models, _
from odoo.exceptions import UserError,AccessError
import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        print(vals_list)
        if type(vals_list)==list:
           analytic_account_id=False
           for v in vals_list:
               if v.get('analytic_account_id'):
                  analytic_account_id=v.get('analytic_account_id')
           for v2 in vals_list:
               if (v2.get('analytic_account_id')==False or 'analytic_account_id' not in v2) and analytic_account_id :
                  v2['analytic_account_id']=analytic_account_id
        return super(AccountMoveLine, self).create(vals_list) 
