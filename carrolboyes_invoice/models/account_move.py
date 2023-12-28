
from odoo import api, fields, models, _

class res_config(models.TransientModel):
    _inherit = "res.config.settings"

    auto_send_mail_invoice = fields.Boolean("Auto Send Mail Invoice",related='company_id.auto_send_mail_invoice',readonly=False)
    auto_validate_invoice = fields.Boolean("Auto Validate Invoice",related='company_id.auto_validate_invoice',readonly=False)

class MagentoGiftVoucher(models.Model):
    _name = "magento.gift.voucher"
    _rec_name = 'giftcard_code'
    _description = 'Magento Voucher'

    giftcard_id = fields.Char(string="Gift Card ID")
    giftcard_code = fields.Char(string="Gift Code")
    order_id = fields.Char(string="Order ID")
    base_giftcard_amount = fields.Float(string="Base Amount")
    giftcard_amount = fields.Float(string="Amount")

class Saleorder(models.Model):
    _inherit = "sale.order"

    gift_voucher_ids = fields.Many2many('magento.gift.voucher', string="Voucher Code")

    @api.model
    def create(self, vals):
        res = super(Saleorder, self).create(vals)
        for invoice in res.invoice_ids:
            invoice.gift_voucher_ids = [(4, x) for x in res.gift_voucher_ids.ids]
        return res

    def _prepare_invoice(self):
        res = super(Saleorder, self)._prepare_invoice()
        if self.gift_voucher_ids:
            res.update({'gift_voucher_ids': [(4, x) for x in self.gift_voucher_ids.ids]})
        return res

class Company(models.Model):
    _inherit = 'res.company'

    auto_validate_invoice = fields.Boolean("Auto Validate Invoice And Send Mail")
    auto_send_mail_invoice = fields.Boolean("Auto Send Mail Invoice")

class AccountInvoice(models.Model):
    _inherit = "account.move"

    picking_id = fields.Many2one('stock.picking','Picking')
    sale_id  =  fields.Many2one('sale.order', 'Sale Origin')
    pur_id   =  fields.Many2one('purchase.order', 'Purchase Origin')
    gift_voucher_ids = fields.Many2many('magento.gift.voucher', string="Voucher Code")


    
