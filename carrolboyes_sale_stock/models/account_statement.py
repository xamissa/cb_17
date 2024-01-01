# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

from odoo import models, fields, api, _

class BankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    # @api.model
    # def _prepare_liquidity_move_line_vals(self):
    #     res = super(BankStatementLine, self)._prepare_liquidity_move_line_vals()
    #     return res


# class AccountReconciliation(models.AbstractModel):
#     _inherit = 'account.reconciliation.widget'

#     @api.model
#     def _get_statement_line(self, st_line):
#         res = super(AccountReconciliation, self)._get_statement_line(st_line)
#         res.update({'analytic_account_id' : st_line.analytic_account_id.id})
#         return res
