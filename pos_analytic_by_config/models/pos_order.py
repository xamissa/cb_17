from odoo import models

class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_lines(self):
        res = super()._prepare_invoice_lines()

        analytic_account = self.session_id.config_id.account_analytic_id
        if analytic_account:
            for line in res:
                line[2].update({"analytic_account_id": analytic_account.id, 'analytic_distribution': {analytic_account.id: 100}})
        return res

    def action_pos_order_invoice(self):
        self_ctx = self.with_context(pos_analytic=True)
        return super(PosOrder, self_ctx).action_pos_order_invoice()
