# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools



class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    change_price = fields.Boolean(string='Change Price')

class PosPriceChangeReport(models.Model):
    _name = "report.pos.price.change"
    _description = "Point of Sale Price Change Report"
    _auto = False
    _order = 'date desc'

    date = fields.Datetime(string='Date', readonly=True)
    order_id = fields.Many2one('pos.order', string='Order', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    user_id = fields.Many2one('res.users', string='Manager', readonly=True)
    unit_price = fields.Float(string='Total Price', readonly=True)
    updated_price = fields.Float(string='Subtotal w/o discount', readonly=True)
    session_id = fields.Many2one('pos.session', string='Session', readonly=True)
    product_qty = fields.Integer(string='Quantity', readonly=True)

    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                l.qty AS product_qty,
                pt.list_price AS unit_price,
                l.price_unit AS updated_price,
                s.id as order_id,
                s.date_order AS date,
                l.product_id AS product_id,
                s.session_id AS session_id,
                s.user_id As user_id
        """

    def _from(self):
        return """
            FROM pos_order_line AS l
                INNER JOIN pos_order s ON (s.id=l.order_id)
                LEFT JOIN product_product p ON (l.product_id=p.id)
                LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                LEFT JOIN uom_uom u ON (u.id=pt.uom_id)
                LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                LEFT JOIN res_company co ON (s.company_id=co.id)
                LEFT JOIN res_currency cu ON (co.currency_id=cu.id)
        """

    def _where(self):
        return """
            WHERE l.change_price IS TRUE
        """

    def _group_by(self):
        return """
            GROUP BY
                s.id,
                s.user_id,
                s.session_id,
                l.product_id,
                p.product_tmpl_id,
                l.qty,
                l.price_unit,
                pt.list_price,
                s.user_id
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._where(), self._group_by())
        )


