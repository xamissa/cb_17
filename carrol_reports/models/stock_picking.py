# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    no_of_cartons = fields.Char(string="Number of Cartons")
    picker_name = fields.Char(string="Picker's Name")
    packer = fields.Char(string="Packer's Name")
    double_checker = fields.Char(string="Double Checker's Name")
    quality_checker = fields.Char(string="Quality Checker's Name")
    waybill_number = fields.Char(string="Waybill Number")
    freight_company = fields.Many2one('freight.company', string="Freight Company")
    freight_mode = fields.Char(string="Freight Mode",related='sale_id.freight_mode')
    on_delivery_addr = fields.Text(string="Customer Delivery Address",related='sale_id.on_delivery_addr')
    client_order_ref = fields.Char(string="Customer Reference",related='sale_id.client_order_ref')
    magento_gift_id = fields.Many2many('magento.gift', related='sale_id.magento_gift_id' , string="Magento Gift")

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        pick_ids = self.search([('group_id', '=', self.group_id.id)])
        if 'no_of_cartons' in vals and vals['no_of_cartons']:
            self._cr.execute("UPDATE stock_picking SET no_of_cartons = %s WHERE id in %s", (vals['no_of_cartons'], tuple(pick_ids.ids)))

        if 'picker_name' in vals and vals['picker_name']:
            self._cr.execute("UPDATE stock_picking SET picker_name = %s WHERE id in %s", (vals['picker_name'], tuple(pick_ids.ids)))

        if 'packer' in vals and vals['packer']:
            self._cr.execute("UPDATE stock_picking SET packer = %s WHERE id in %s", (vals['packer'], tuple(pick_ids.ids)))

        if 'double_checker' in vals and vals['double_checker']:
            self._cr.execute("UPDATE stock_picking SET double_checker = %s WHERE id in %s", (vals['double_checker'], tuple(pick_ids.ids)))

        if 'quality_checker' in vals and vals['quality_checker']:
            self._cr.execute("UPDATE stock_picking SET quality_checker = %s WHERE id in %s", (vals['quality_checker'], tuple(pick_ids.ids)))

        #if 'waybill_number' in vals and vals['waybill_number']:
        #    self._cr.execute("UPDATE stock_picking SET waybill_number = %s WHERE id in %s", (vals['waybill_number'], tuple(pick_ids.ids)))

        if 'freight_company' in vals and vals['freight_company']:
            self._cr.execute("UPDATE stock_picking SET freight_company = %s WHERE id in %s", (vals['freight_company'], tuple(pick_ids.ids)))
        return res

    def print_invoice(self):
        if self.picking_type_id.name == 'Pack' and self.state == 'done':
            return self.env.ref('carrol_reports.action_invoice_print_report').report_action(self)
        else:
            raise ValidationError(_('This picking is not allowed to print invoice report'))

    def _get_price_unit(self,line):
        #for mv_line in self.move_line_ids_without_package:
        price_unit = 0.0
        for s_line in self.sale_id.order_line:
           if line.product_id.id == s_line.product_id.id:
                price_unit = s_line.price_unit
        return '{:,.2f}'.format(price_unit)

    def _get_amount(self,line):
        amount = 0.0
        #for mv_line in self.move_line_ids_without_package:
        for s_line in self.sale_id.order_line:
            if line.product_id.id == s_line.product_id.id:
                #amount = s_line.price_subtotal
                amount = line.quantity * s_line.price_unit
        return '{:,.2f}'.format(amount)


    def _get_tax_price(self,line):
        tax = 0.0
        for s_line in self.sale_id.order_line:
            if line.product_id.id == s_line.product_id.id:
                #tax = s_line.price_tax
                tax = s_line.price_unit
        tax = tax * 0.15
        return '{:,.2f}'.format(tax)

    def _get_subtotal(self):
        subtotal = 0.0
        product=[]
        for mv_line in self.move_line_ids_without_package:
            for s_line in self.sale_id.order_line:
                if mv_line.product_id.id == s_line.product_id.id and mv_line.product_id.id not in product:
                    product.append(s_line.product_id.id)
                    subtotal = subtotal + (mv_line.quantity * s_line.price_unit)
                
        return '{:,.2f}'.format(subtotal)

    def _get_total_tax(self):
        total_tax = 0.0
        subtotal = 0.0
        product=[]
        for mv_line in self.move_line_ids_without_package:
            for s_line in self.sale_id.order_line:
                if mv_line.product_id.id == s_line.product_id.id and mv_line.product_id.id not in product:
                    product.append(s_line.product_id.id)
                    subtotal = subtotal + (mv_line.quantity * s_line.price_unit)
        subtotal = subtotal * 0.15
        total_tax = subtotal 
        return '{:,.2f}'.format(total_tax)

    def _get_total(self):
        total = 0.0
        subtotal = 0.0
        total_tax = 0.0
        product=[]
        for mv_line in self.move_line_ids_without_package:
            for s_line in self.sale_id.order_line:
                if mv_line.product_id.id == s_line.product_id.id  and mv_line.product_id.id not in product:
                    product.append(s_line.product_id.id)
                    #total = total + s_line.price_subtotal
                    subtotal = subtotal + (mv_line.quantity * s_line.price_unit)
                    #total_tax = total_tax + s_line.price_tax

        total_tax = subtotal * 0.15
        total = subtotal + total_tax
        #total = total + (total*0.15)
        return '{:,.2f}'.format(total)


class FreightCompany(models.Model):
    _name = "freight.company"
    _description = "Freight Company"

    name = fields.Char(string="Name")

# class ProductTemplate(models.Model):
#     _inherit = "product.template"

#     spaces = fields.Text(string="Spaces")

