# -*- coding: utf-8 -*-
from odoo import fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account', related='order_id.analytic_account_id', required=True)

    def _prepare_procurement_values(self,group_id):
        res = super(SaleOrderLine,self)._prepare_procurement_values(group_id=group_id)
        # tag_ids = []
        # for tag in self.analytic_tag_ids:
        #     tag_ids.append(tag.id)
        res.update({
            'analytic_account_id':self.order_id.analytic_account_id.id,
            'analytic_distribution': {self.order_id.analytic_account_id.id: 100},
            #'tag_ids':[(6,0,tag_ids)],
            })
        return res

