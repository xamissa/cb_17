# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        action = super(StockPicking, self)._action_done()
        if len(self) == 1:
            for picking in self:
                if picking.state == 'done'  :
                    if picking.picking_type_id.code == 'incoming' and 'Return of' in picking.origin:
                        inv_obj = self.env['account.move']
                        invoice_lines =[]
                        invoice_vals = []
                        sale_order_line_obj = self.env['account.move.line']
                        #sale_order  =  self.env['sale.order'].search([('id', '=',picking.origin)],limit=1)
                        sale_id = picking.sale_id
                        print("SALEEEEEEEEE", sale_id.read())
                        #journal = self.env['account.move'].with_context(default_move_type='out_refund')._get_default_journal()
                        journal = self.env['account.journal'].browse(1)
                        if not journal:
                            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (picking.company_id.name, picking.company_id.id))
                        
                        #if sale_id and not sale_id.magento_order_id:
                        if sale_id:
                            vals  = {
                                'invoice_origin': picking.origin,
                                # 'picking_id':picking.id,
                                'move_type': 'out_refund',
                                'ref': picking.client_order_ref or '' + picking.name,
                                'currency_id' : sale_id.currency_id.id,
                                # 'sale_id':sale_id.id,
                                'journal_id': journal.id,  
                                'partner_id': picking.partner_id.id,
                                
                                'invoice_payment_term_id': sale_id.payment_term_id.id,
                                'fiscal_position_id': sale_id.fiscal_position_id.id or sale_id.partner_id.property_account_position_id.id,
                                'team_id': sale_id.team_id.id,
                                'invoice_date' : fields.Datetime.now().date(),
                                'invoice_user_id' : sale_id.user_id and sale_id.user_id.id,
                                #'magento_payment_method_id': sale_id.magento_payment_method_id and sale_id.magento_payment_method_id.id
                            }
                            print("VALSSSSSSSSSS", vals)
                            
                            if not sale_id.partner_id.property_payment_term_id:
                                sale_id.partner_id.property_payment_term_id = sale_id.payment_term_id.id
                            invoice = inv_obj.create(vals)
                            print("INVOICEEEEEEEEE", invoice)
                            import pdb
                            pdb.set_trace()
                            for so_line in  sale_id.order_line :
                                if so_line.product_id:
                                    if so_line.product_id.type == "service":
                                        if so_line.product_uom_qty != so_line.qty_invoiced:
                                            if so_line.product_id.property_account_income_id:
                                                account_id = so_line.product_id.property_account_income_id
                                            elif so_line.product_id.categ_id.property_account_income_categ_id:
                                                account_id = so_line.product_id.categ_id.property_account_income_categ_id                    
                                            elif journal.default_account_id:
                                                account_id = journal.default_account_id
                                            else:
                                                raise UserError(_('Please define an account for the Product/Category.'))
                                            inv_line = {
                                                    'name': so_line.name,
                                                    'product_id': so_line.product_id.id,
                                                    'product_uom_id': so_line.product_id.uom_id.id,
                                                    'quantity': -(so_line.qty_invoiced) if so_line.product_id.id == 8738 else so_line.product_uom_qty,
                                                    'account_id': account_id.id,
                                                    'analytic_account_id': so_line.analytic_account_id.id,
                                                    'display_type': so_line.display_type,
                                                    'tax_ids': [(6, 0, so_line.tax_id.ids)],
                                                    'discount': so_line.discount,
                                                    # 'mag_discount_amt': so_line.mag_discount_amt,
                                                    'display_type': 'product',
                                                    'move_id':invoice.id,
                                                    'price_unit': so_line.price_unit,
                                                    'sale_line_ids': [(4, so_line.id)],
                                                    }
                                            invoice_vals.append((0,0,inv_line))
                                            so_line.write({
                                                'qty_to_invoice':so_line.product_uom_qty
                                            })                                
                                    else:
                                        if so_line.product_id.property_account_income_id:
                                            account = so_line.product_id.property_account_income_id
                                        elif so_line.product_id.categ_id.property_account_income_categ_id:
                                            account = so_line.product_id.categ_id.property_account_income_categ_id
                                        else:
                                            account = self.env['ir.property']._get('property_account_income_categ_id', 'product.category')
                                        if not account :
                                            raise UserError(_('Please define an account for the Product/Category.'))
    
                                        route = False
                                        if self._context.get('flag') == True:
                                            pass
                                        else:
                                            if so_line.product_id.invoice_policy == 'delivery':  
                                                for i in picking.move_ids_without_package.filtered(lambda x : x.sale_line_id == so_line and x.product_id == so_line.product_id and x.state == 'done'):
                                                    inv_line = {
                                                            'name': so_line.name,
                                                            'product_id': so_line.product_id.id,
                                                            'product_uom_id': so_line.product_id.uom_id.id,
                                                            'quantity': i.quantity_done,
                                                            'account_id': account.id,
                                                            'display_type': 'product',
                                                            
                                                            'tax_ids': [(6, 0, so_line.tax_id.ids)],
                                                            'discount': so_line.discount,
                                                            #'mag_discount_amt': so_line.mag_discount_amt,
                                                            'move_id':invoice.id,
                                                            'price_unit': so_line.price_unit,
                                                            'sale_line_ids': [(4, so_line.id)],
                                                            }
                                                    invoice_vals.append((0,0,inv_line))

                                                    so_line.write({'qty_to_invoice':so_line.product_uom_qty})
                                            else:
                                                inv_line = {
                                                        'name': so_line.name,
                                                        'product_id': so_line.product_id.id,
                                                        'product_uom_id': so_line.product_id.uom_id.id,
                                                        'quantity': so_line.product_uom_qty,
                                                        'account_id': account.id,
                                                        'display_type': 'product',
                                                        'tax_ids': [(6, 0, so_line.tax_id.ids)],
                                                        'discount': so_line.discount,
                                                       # 'mag_discount_amt': so_line.mag_discount_amt,
                                                        'move_id':invoice.id,
                                                        'price_unit': so_line.price_unit,
                                                        'sale_line_ids': [(4, so_line.id)],
                                                        }
                                                print("INVOICEEEEEEEEE", invoice_vals)
                                                print("LINEEEEEEEEEEEEE", inv_line)
                                                invoice_vals.append((0,0,inv_line))
                                                
                                                so_line.write({'qty_to_invoice':so_line.product_uom_qty})
                            invoice.write({
                                'invoice_line_ids' : invoice_vals
                            })
                            #if invoice and invoice.magento_payment_method_id:
                            if invoice:
                                if invoice.invoice_line_ids:
                                    invoice.action_post()     
            return action

