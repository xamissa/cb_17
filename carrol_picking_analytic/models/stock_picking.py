# -*- coding: utf-8 -*-
from odoo import fields, models, _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        sale_list=[]
        ref = self.name
        sale_analytic_dict={}
        purchase_analytic_dict={}
        if self.sale_id :
            for line in self.move_ids_without_package:
                if line.analytic_account_id and line.sale_line_id:
                    # tag_ids = []
                    # for tag_id in line.tag_ids:
                    #     tag_ids.append(tag_id.id)
                    _logger.info("button_validate============= %s",line)
                    sale_analytic_dict.update({
                        'name': line.sale_line_id.product_id.name or line.product_id.name,
                        'amount': line.sale_line_id.price_unit,
                        'product_id': line.sale_line_id.product_id.id,
                        'product_uom_id': line.sale_line_id.product_uom.id,
                        'date': line.date_deadline or line.date,
                        'account_id': line.analytic_account_id.id,
                        'unit_amount': line.quantity,
                        'general_account_id': self.partner_id.property_account_receivable_id.id,
                        'ref': ref,
                        #'tag_ids':[(6,0,tag_ids)],
                        #'group_id': line.analytic_account_id.group_id and line.analytic_account_id.group_id.id
                    })
                    _logger.info("sale_analytic_dict>>>>>>>>>>>>>>> %s",sale_analytic_dict)
                    self.env['account.analytic.line'].create(sale_analytic_dict)

        if self.purchase_id :
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                   # tag_ids = []    
                   # for tag_id in line.tag_ids:
                   #      tag_ids.append(tag_id.id)  

                   purchase_analytic_dict.update({
                        'name': line.purchase_line_id.product_id.name,
                        'date': line.date_deadline,
                        'account_id': line.analytic_account_id.id,
                        'unit_amount': line.quantity,
                        'amount': (line.product_id.standard_price *line.quantity) * -1,
                        'product_id': line.purchase_line_id.product_id.id,
                        'product_uom_id': line.purchase_line_id.product_uom.id,
                        'general_account_id': self.partner_id.property_account_payable_id.id,
                        'ref': ref,
                        #'tag_ids':[(6,0,tag_ids)]
                    })

                   self.env['account.analytic.line'].create(purchase_analytic_dict)


        if not self.purchase_id and not self.sale_id:
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                   # tag_ids =[]
                   # for tag_id in line.tag_ids:
                   #      tag_ids.append(tag_id.id)  

                   purchase_analytic_dict.update({
                    
                        'name': line.product_id.name,
                        'date': datetime.now(),
                        'account_id': line.analytic_account_id.id,
                        'unit_amount': line.quantity,
                        'amount': line.product_id.lst_price * line.quantity,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'general_account_id': self.partner_id.property_account_receivable_id.id,
                        'ref': ref,
                        #'tag_ids':[(6,0,tag_ids)] 
                    })
                   if self.picking_type_id.code == 'incoming':
                       purchase_analytic_dict['amount']= (line.product_id.standard_price *line.quantity) * -1 
                             
                   self.env['account.analytic.line'].create(purchase_analytic_dict)
        return super(StockPicking, self).button_validate()


        
