# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    freight_mode = fields.Char(string="Freight Mode")
    on_delivery_addr = fields.Text(string="Customer Delivery Address")
    magento_gift_id = fields.Many2many('magento.gift', string="Magento Gift")
    discount_description = fields.Text(string="Discount Description")

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    street = fields.Char(string="Street")
    phone = fields.Char(string="Phone")

