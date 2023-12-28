# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    tag_ids  = fields.Many2many('account.analytic.tag', string= 'Tag')

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        tag_ids = []
        for tag in self.tag_ids:
            tag_ids.append(tag.id)

        rslt = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description)
        if self.analytic_account_id:
            rslt['debit_line_vals']['analytic_account_id']= self.analytic_account_id.id
            rslt['credit_line_vals']['analytic_account_id']= self.analytic_account_id.id

        if tag_ids:
            rslt['debit_line_vals']['analytic_tag_ids']= [(6,0,tag_ids)]
            rslt['credit_line_vals']['analytic_tag_ids']= [(6,0,tag_ids)]

        return rslt
