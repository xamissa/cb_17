##############################################################################
#
#    ERP WEB
#
##############################################################################
from odoo.tools.translate import _
from odoo.osv import osv
from odoo import api, fields, models


class sale_order_confirm(models.TransientModel):
    _name = "sale.order.confirm"
    _description = "Sale Order"

    def confim_orders(self):
        print("R%%%%%%%%%%%%%%%%%%%%")
        sale_obj = self.env['sale.order']
        sale_ids = sale_obj.browse(self._context.get('active_ids'))
        part_obj = self.env['res.partner']
        context = (self._context or {})
        if not self.env['res.users'].has_group('erpweb_credit_limit_v14.group_order_confirm'):
            raise osv.except_osv(_('User Error!'), _('You can not confirm sale order'))
        else:
            allow_popup = sale_ids.with_context(sale=sale_ids).action_popup()
            if allow_popup:
                return allow_popup
            sale_ids.with_context(ignore=True).action_confirm()
            message = ("Your credit limit exceeded. But still validated by "+str(self.env.user.name))
            sale_ids.message_post(body=message)
            if context.get('send_email'):
                sale_obj.force_quotation_send(sale_ids, context=context)
        return True


    def confim_picking(self):
        stock_obj = self.env['stock.picking']
        picking_ids = stock_obj.browse(self._context.get('active_ids'))
        
        context = (self._context or {})
        if not self.env['res.users'].has_group('erpweb_credit_limit_v14.group_order_confirm'):
            raise osv.except_osv(_('User Error!'), _('Credit limit exceeded. You can not confirm Picking'))
        else:
            picking_ids.with_context(ignore=True).button_validate()
            message = ("Your credit limit exceeded. But still validated by "+str(self.env.user.name))
            picking_ids.message_post(body=message)
        return True

    def confim_invoices(self):
        move_obj = self.env['account.move']
        move_ids = move_obj.browse(self._context.get('active_ids'))
        
        context = (self._context or {})
        if not self.env['res.users'].has_group('erpweb_credit_limit_v14.group_order_confirm'):
            raise osv.except_osv(_('User Error!'), _('Credit limit exceeded. You can not confirm Picking'))
        else:
            move_ids.with_context(ignore=True).action_invoice_open()
            message = ("Your credit limit exceeded. But still validated by "+str(self.env.user.name))
            move_ids.message_post(body=message)
        return True

class SaleCreditLimit(models.TransientModel):
    _name = "sale.credit.limit"
    _description = "Sales Credit Limit Exceeds"

    def button_ok(self):
        active_id = self.env.context['active_ids']
        sale_id=self.env['sale.order'].browse(active_id)
        message = ("Your credit limit exceeded.")
        sale_id.message_post(body=message)
        return {'type': 'ir.actions.act_window_close'}

