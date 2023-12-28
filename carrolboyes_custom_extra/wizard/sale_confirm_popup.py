##############################################################################
#
#    ERP WEB
#
##############################################################################
from odoo.tools.translate import _
from odoo.osv import osv
from odoo import api, fields, models


class sale_confirm_popup(models.TransientModel):
    _name = "sale.confirm.popup"
    _description = "Sale Order"

    prd_lst = fields.Char(readonly=True)
    loc_lst = fields.Char(readonly=True)

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        p_list = []
        if self._context.get('pl_lst'):
            for p in self._context.get('pl_lst'):
                if p:
                    p_list.append(p['prd'] +'-'+ p['loc'])
            res['prd_lst'] = str(p_list)[1:-1]
        return res

    def sale_order_confirm(self):
        sale_obj = self.env['sale.order']
        if self._context.get('sale'):
            sale_ids = sale_obj.browse(self._context.get('sale'))
        else:
            sale_ids = sale_obj.browse(self._context.get('active_ids'))
        #sale_ids.action_confirm()
        return sale_ids.with_context(popup=True).action_confirm()

