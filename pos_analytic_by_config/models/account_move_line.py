from odoo import api, models, fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, store=True, readonly=False, check_company=True, copy=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        analytic_account_id = self.analytic_account_id
        analytic_distribution = self.analytic_distribution
        res = super()._onchange_product_id()
        if not self.env.context.get("pos_analytic") or not analytic_account_id or not analytic_distribution:
            return res
        if self.analytic_account_id != analytic_account_id:
            self.analytic_account_id = analytic_account_id
            self.analytic_distribution = {analytic_account_id.id: 100}
        return res
