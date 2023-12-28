from odoo import api, fields, models, _

class PosSession(models.Model):
    _inherit = "pos.session"

    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account", related='config_id.account_analytic_id', store="True",string="Analytic Account"
    )

    def _credit_amounts(self, partial_move_line_vals, amount, amount_converted, force_company_currency=False):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            partial_move_line_vals.update({"analytic_account_id": account_analytic_id.id, 'analytic_distribution': {account_analytic_id.id: 100}})
        return super()._credit_amounts(partial_move_line_vals, amount, amount_converted, force_company_currency)

    def _debit_amounts(self, partial_move_line_vals, amount, amount_converted, force_company_currency=False):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            partial_move_line_vals.update({"analytic_account_id": account_analytic_id.id, 'analytic_distribution': {account_analytic_id.id: 100}})
        return super()._debit_amounts(partial_move_line_vals, amount, amount_converted, force_company_currency)

    def _create_account_move(self):
        res = super(PosSession, self)._create_account_move()
        for line in self.move_id.line_ids:
            line.analytic_account_id = self.account_analytic_id
            line.analytic_distribution = {self.account_analytic_id.id: 100}
        return res

    def _reconcile_account_move_lines(self, data):
        print("_reconcile_account_move_lines>>>>>>>>>>>>>>>")
        res = super(PosSession, self)._reconcile_account_move_lines(data)
        # reconcile cash receivable lines
        split_cash_statement_lines = data.get('split_cash_statement_lines')
        combine_cash_statement_lines = data.get('combine_cash_statement_lines')
        split_cash_receivable_lines = data.get('split_cash_receivable_lines')
        combine_cash_receivable_lines = data.get('combine_cash_receivable_lines')
        # order_account_move_receivable_lines = data.get('order_account_move_receivable_lines')
        # invoice_receivable_lines = data.get('invoice_receivable_lines')
        # stock_output_lines = data.get('stock_output_lines')

        for statement in self.statement_ids:
            all_lines = (
                  split_cash_statement_lines[statement].mapped('move_id.line_ids')
                | combine_cash_statement_lines[statement].mapped('move_id.line_ids')
                | split_cash_receivable_lines[statement]
                | combine_cash_receivable_lines[statement]
            )
            for line in all_lines:
                line.analytic_account_id = self.account_analytic_id
                line.analytic_distribution = {self.account_analytic_id.id: 100}

        pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
        pickings |= self.order_ids.filtered(lambda o: not o.is_invoiced).mapped('picking_ids')
        stock_moves = self.env['stock.move'].search([('picking_id', 'in', pickings.ids)])
        stock_account_move_lines = self.env['account.move'].search([('stock_move_id', 'in', stock_moves.ids)]).mapped('line_ids')
        stock_account_move_lines.write({'analytic_account_id': self.account_analytic_id, 'analytic_distribution': {self.account_analytic_id.id: 100}})
        return res

class AccountBankStatementline(models.Model):
    _inherit = 'account.bank.statement.line'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account') #currently available in carrolboyes_sale_stock module

    @api.model
    def create(self, values):
        res = super(AccountBankStatementline, self).create(values)
        if res.statement_id.pos_session_id:
          res.analytic_account_id=res.statement_id.pos_session_id.account_analytic_id.id
        return res

class Accountmoveline(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, values):
        res = super(Accountmoveline, self).create(values)
        for r in res:
          if (not r.analytic_account_id or not r.analytic_distribution) and r.statement_id:
            if r.statement_id.pos_session_id:
              r.analytic_account_id=r.statement_id.pos_session_id.account_analytic_id.id
              r.analytic_distribution = {r.statement_id.pos_session_id.account_analytic_id.id: 100}
        return res
