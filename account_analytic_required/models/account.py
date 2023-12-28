from odoo import _, api, exceptions, fields, models
from odoo.tools import float_is_zero


class AccountAccount(models.Model):
    _inherit = "account.account"

    analytic_req = fields.Boolean(string= "Analytic Required",default= False)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_req = fields.Boolean(related='account_id.analytic_req')    

class AccountAsset(models.Model):
    _inherit = "account.asset"

    @api.onchange('model_id')
    def _onchange_model_id(self):
        model = self.model_id
        if model:
            self.method = model.method
            self.method_number = model.method_number
            self.method_period = model.method_period
            self.method_progress_factor = model.method_progress_factor
            self.prorata = model.prorata
            self.prorata_date = fields.Date.today()
            if model.account_analytic_id:
                self.account_analytic_id = model.account_analytic_id.id

            if model.analytic_tag_ids:
                self.analytic_tag_ids = [(6, 0, model.analytic_tag_ids.ids)]
            self.account_depreciation_id = model.account_depreciation_id
            self.account_depreciation_expense_id = model.account_depreciation_expense_id
            self.journal_id = model.journal_id
            self.account_asset_id = model.account_asset_id
