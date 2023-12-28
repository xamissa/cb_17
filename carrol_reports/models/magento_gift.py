# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MagentoGift(models.Model):
    _name = "magento.gift"
    _rec_name = 'recipient'
    _description = 'Magento Gift'

    gift_message_id = fields.Char(string="Gift Message ID")
    customer_id = fields.Many2one("res.partner", string="Customer")
    sender = fields.Char(string="Sender")
    recipient = fields.Char(string="Recipient")
    message = fields.Char(string="Message")
    product = fields.Char(string="Product")
    sku = fields.Char(string="SKU")