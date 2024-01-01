from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.osv import osv
from odoo.tools import float_is_zero, float_compare
import logging

_logger = logging.getLogger(__name__)
class account_payment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res=super(account_payment, self).action_post()
        for rec in self:
            if rec.partner_type=='customer' and rec.partner_id and rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id==1:
               pick=self.env['stock.picking'].search([('partner_id','=',rec.partner_id.id),('state','in',['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])])
               if not pick:
                   partner_ids = self.env['res.partner'].search([('parent_id', '=', rec.partner_id.id)])
                   pick=self.env['stock.picking'].search([('partner_id','in',partner_ids.ids),('state','in',['draft', 'waiting', 'partially_available', 'assigned', 'confirmed']),('location_dest_id.usage', '=', 'customer')])
               pick._get_payment_state()
        return res

# class AccountReconciliation(models.AbstractModel):
#     _inherit = 'account.reconciliation.widget'
#     @api.model
#     def process_bank_statement_line(self, st_line_ids, data):
#         bsl_dict = super(AccountReconciliation, self).process_bank_statement_line(st_line_ids, data)
#         st_line_ids = bsl_dict.get('statement_line_ids')
#         for rec in st_line_ids:
#             if rec.partner_id.customer_rank > 0 and rec.partner_id and rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id==1:
#                pick=self.env['stock.picking'].search([('partner_id','=',rec.partner_id.id),('state','in',['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])])
#                if not pick:
#                    partner_ids = self.env['res.partner'].search([('parent_id', '=', rec.partner_id.id)])
#                    pick=self.env['stock.picking'].search([('partner_id','in',partner_ids.ids),('state','in',['draft', 'waiting', 'partially_available', 'assigned', 'confirmed']),('location_dest_id.usage', '=', 'customer')])
#                pick._get_payment_state()
#         return bsl_dict

class BankRecWidget(models.Model):
    _inherit = "bank.rec.widget"

    # TODO: needs to check
    def _action_validate(self):
        super(BankRecWidget, self)._action_validate()
        for rec in self.st_line_id:
            if rec.partner_id.customer_rank > 0 and rec.partner_id and rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id==1:
                pick=self.env['stock.picking'].search([('partner_id','=',rec.partner_id.id),('state','in',['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])])
                if not pick:
                    partner_ids = self.env['res.partner'].search([('parent_id', '=', rec.partner_id.id)])
                    pick=self.env['stock.picking'].search([('partner_id','in',partner_ids.ids),('state','in',['draft', 'waiting', 'partially_available', 'assigned', 'confirmed']),('location_dest_id.usage', '=', 'customer')])
                pick._get_payment_state()

class res_partner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float('Credit Limit')
    over_limit = fields.Boolean('Ignore Credit Control', default=False)
    cr_limit_access = fields.Boolean(compute='_get_access_rights',string="Credit limit access")
    # property_payment_term_id = fields.Many2one('account.payment.term', track_visibility='onchange',tracking=100)
    # property_supplier_payment_term_id = fields.Many2one('account.payment.term', track_visibility='onchange')

    @api.depends('name')
    def _get_access_rights(self):
        user_grp = self.env.user.has_group( "erpweb_credit_limit_v14.credit_limit_access") 
        if user_grp:
            self.cr_limit_access = True
        else:
            self.cr_limit_access = False  

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_status = fields.Char(compute='_get_payment_state',string="Payment Status",store=True)

    @api.depends('partner_id.credit')
    def _get_payment_state(self):

        for picking in self:
            picking.invoice_status = ''
            credit = 0.0
            if picking.sale_id.partner_id.commercial_partner_id.credit:
                credit = picking.sale_id.partner_id.commercial_partner_id.credit

            if picking.sale_id and credit < 0 and picking.location_dest_id.usage=='customer' and picking.sale_id.payment_term_id.id==1:
               credit_limit=picking.sale_id.partner_id.credit_limit + abs(credit)
               if credit_limit >= picking.sale_id.amount_total:
                  picking.invoice_status = 'Paid'
               else:
                  picking.invoice_status = 'Not Paid' 
                  #picking.invoice_status = 'Awating for Payment'
            if picking.sale_id and credit==0 and picking.location_dest_id.usage=='customer' and picking.sale_id.payment_term_id.id==1:
                  picking.invoice_status = 'Not Paid'
            if picking.sale_id and credit>0 and picking.location_dest_id.usage=='customer' and picking.sale_id.payment_term_id.id==1:
                  picking.invoice_status = 'Not Paid'

            # odoo_magento2_ept needed
            # if picking.sale_id.magento_order_id and picking.location_dest_id.usage=='customer':
            #     picking.invoice_status = 'Paid'

    def ignore_credit_limit(self):
        res= self.with_context(ignore=True).button_validate()
        if self.sale_id and self.sale_id.payment_term_id.id==1 and self.location_dest_id.usage=='customer':
            message = ("Your credit limit exceeded. But still validated by "+str(self.env.user.name))
            self.message_post(body=message)
        return res

    def button_validate(self):
        self.ensure_one()
        today_date = fields.Date.today()
        credit_limit = 0
        credit1 = 0

        if self.sale_id.partner_id.commercial_partner_id.credit:
            credit1 = self.sale_id.partner_id.commercial_partner_id.credit
        
        if self.partner_id.over_limit:
            return super(StockPicking, self).button_validate()

        context = (self._context or {})
        if context.get('ignore'):
            return super(StockPicking, self).button_validate()

        if self.sale_id and self.sale_id.payment_term_id.id == 1 and self.location_dest_id.usage == 'customer' and self.sale_id.partner_id.credit_limit == 0.0 and credit1 == 0.0: #and not self.sale_id.magento_order_id:
          raise UserError(_('You cannot validate delivery order, sales order not paid.'))

        
        if self.sale_id and self.sale_id.payment_term_id.id == 1 and self.location_dest_id.usage=='customer':
            
            tran_id=self.env['payment.transaction'].search([('sale_order_ids','in',[self.sale_id.id]),('state','=','done')])
            if tran_id:
                return super(StockPicking,self).button_validate()

            if self.sale_id.team_id :
                if self.sale_id.team_id.name == 'Website' and sale.require_payment==True:
                    return super(StockPicking, self).button_validate()
            
            if self.sale_id.partner_id and self.location_dest_id.usage=='customer':
                # deduct the invoiced amount
                if self.sale_id.partner_id.credit_limit and credit1 > 0:
                    credit_limit = self.sale_id.partner_id.credit_limit - credit1

                if credit1 < 0:
                    credit_limit=self.sale_id.partner_id.credit_limit + abs(credit1)

                if self.sale_id.partner_id.credit_limit and credit1 == 0:
                    credit_limit = self.sale_id.partner_id.credit_limit



                # deduct total sales order not done or not paid yet
                self.env.cr.execute("select sum(amount_total),sum(invoiced_amount) from sale_order where state in ('sale','done')\
                                 and partner_id = %s and invoice_status!='invoiced' ", (self.sale_id.partner_id.id, ))

                res_part = self.env.cr.fetchone()

                if self.sale_id.partner_id.credit_limit != 0 or credit1 != 0:
                    if res_part and res_part[0] is not None and res_part[1] is not None:
                        if (credit_limit - (res_part[0]- res_part[1])) < 0:
                            raise UserError(_("""Customer credit limit exceeded """ ))

                    if res_part and res_part[0] is not None and res_part[1] is None:
                        if (credit_limit - res_part[0]) < 0:
                            raise UserError(_("""Customer credit limit exceeded """ ))

                #check any overdue invoice
                self.env.cr.execute("select sum(amount_residual) from account_move where payment_state = 'not_paid'\
                                 and partner_id = %s and invoice_date_due < %s and move_type = 'out_invoice' ", (self.sale_id.partner_id.id, today_date))

                invoice_part = self.env.cr.fetchone()
                if invoice_part and invoice_part[0]:
                    raise UserError(_("""Customer having some overdue invoices, please resolve those.""" ))

        return super(StockPicking, self).button_validate()

class sale_order(models.Model):
    _inherit = 'sale.order'

    invoiced_amount = fields.Float('Invoiced Amount', compute="_compute_invoiced_amount", store=True)
    after_invoice_amount = fields.Float('To Invoice', compute="_compute_invoiced_amount")

    @api.depends('invoice_ids')
    def _compute_invoiced_amount(self):
        for sale in self:
            total = 0.0
            total_draft_invoice = 0.0
            if sale.invoice_ids:
                for invoice in sale.invoice_ids:
                    if invoice.move_type == 'out_invoice':
                        total += invoice.amount_total
                    elif invoice.move_type == 'out_refund':
                        total -= invoice.amount_total

            sale.invoiced_amount = total
            sale.after_invoice_amount = sale.amount_total - total

    def action_popup(self):
        for res in self:
            prd_lst = []
            loc_lst = []
            context1 = {}
            prd_loc_dict = {}
            prd_loc_list = []
            for line in res.order_line.filtered(lambda x: x.product_id.type == 'product'):
                quant_obj = self.env['stock.quant']
                if line.route_id:
                    loc_id = line.route_id.rule_ids[0].location_src_id
                else:
                    loc_id = line.order_id.warehouse_id.lot_stock_id
                qty_available = quant_obj._get_available_quantity(line.product_id, loc_id)
                if qty_available < line.product_uom_qty:
                    prd_lst.append(line.product_id.name)
                    prd_loc_dict = {'prd':line.product_id.name, 'loc':loc_id.display_name}
                    if loc_id.display_name not in loc_lst:
                        loc_lst.append(loc_id.display_name)
                prd_loc_list.append(prd_loc_dict)
            if prd_lst:
                action = self.env.ref('carrolboyes_custom_extra.action_confirm_popup_sale_orders').read()[0]
                if self._context.get('sale'):
                    #action['context'] = dict(sale=self._context.get('sale').id,prd_lst=prd_lst)
                    context1 = {'sale':self._context.get('sale').id}
                context1.update({'prd_lst':prd_lst})
                context1.update({'loc_lst':loc_lst})
                context1.update({'pl_lst':prd_loc_list})
                action['context'] = context1
                return action
        return False

    def action_confirm(self):
        flag = False
        flag2 = False
        over_limit=False
        context = (self._context or {})
        part_obj = self.env['res.partner']
        if not context:
            context = {}
        #assert len(self.ids) == 1, 'This option should only be used for a single id at a time.'
        credit_limit = 0.0
        sa_war=''
        today_date = fields.Date.today()
        allow_popup = False
        for sale in self:
            _logger.info("************************%s",context)

            # TODO: takealot_odoo
            # if sale.po_number:
            #     return super(sale_order,self).action_confirm()
            
            # TODO: odoo_magento2_ept
            # if sale.magento_order_id:
            #     return super(sale_order,self).action_confirm()
            if context.get('popup'):
                return super(sale_order,self).action_confirm()
            if context.get('ignore'):
                allow_popup = True
                #return super(sale_order,self).action_confirm()
            if sale.team_id:
                if sale.team_id.name == 'Website':
                    allow_popup = True
                    #return super(sale_order, self).action_confirm()

            if allow_popup:
                popup1 = sale.action_popup()
                if popup1:
                    return popup1
                return super(sale_order,self).action_confirm()

            if not sale.payment_term_id:
                  raise UserError(_("""You cannot validate order without payment terms.""" ))

            over_limit=sale.partner_id.over_limit
            self.env.cr.execute("select sum(amount_total),sum(invoiced_amount) from sale_order where state in ('sale','done')\
                         and partner_id = %s and invoice_status!='invoiced' ", (sale.partner_id.id, ))
            res_part = self.env.cr.fetchone()

            if sale.partner_id.credit_limit == 0.0 and sale.partner_id.credit < 0:
                return super(sale_order, self).action_confirm()

            if sale.partner_id.credit_limit and sale.partner_id.credit>0:
                credit_limit = sale.partner_id.credit_limit - sale.partner_id.credit
            if sale.partner_id.credit_limit and sale.partner_id.credit<0:
                credit_limit=sale.partner_id.credit_limit + abs(sale.partner_id.credit)

            if sale.partner_id.credit_limit and sale.partner_id.credit == 0:
                credit_limit = sale.partner_id.credit_limit

            if res_part and res_part[0] is not None and res_part[1] is not None:
                credit_limit = credit_limit - (res_part[0]- res_part[1])

            if res_part and res_part[0] is not None and res_part[1] is None:
                credit_limit = credit_limit - res_part[0]

            if sale.amount_total > credit_limit:
                flag = True
                #sa_war='Sale ' +sale.name  + ' Partner Name' +sale.partner_id.name
            #if res:
            #    flag = True
                #raise osv.except_osv(_('User Error!'), _('You cannot validate outside payment terms.'))
#        view = self.env.ref('erpweb_credit_limit_v11.view_import_sale_order')

            if sale.partner_id.credit_limit == 0 and sale.partner_id.credit == 0:
                flag= False

            #check any overdue invoice
            self.env.cr.execute("select sum(amount_residual) from account_move where payment_state = 'not_paid'\
                             and partner_id = %s and invoice_date_due < %s and move_type = 'out_invoice' ", (sale.partner_id.id, today_date))

            invoice_part = self.env.cr.fetchone()

            if invoice_part and invoice_part[0] is not None:
                flag2 = True
        _logger.info('%s %s %s %s %s::::::::::::::::::::::::::::',credit_limit,over_limit,flag,flag2,invoice_part)
        over_limit= False

        if over_limit==False and sale.payment_term_id.id!=1:
            if credit_limit == 0.0:
                wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_credit_limit_v14.view_import_sale_order')
                return {
                    'name':"Sale Credit Limit Exceed",
                    'view_mode': 'form',
                    'view_id': wizard_form,
                    'view_type': 'form',
                    'res_model': 'sale.order.confirm',
                    'type': 'ir.actions.act_window',
                    'target': 'new'
                        }
                
                #raise UserError(_("""Credit Limit Exceed for the Customer!""" ))

            if flag==True and flag2==True and  sale.payment_term_id.id!=1:
                _logger.info('I am inside===>>%s----%s',flag, flag2)
                wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_credit_limit_v14.view_import_sale_order')
                return {
                        'name':"Sale Credit Limit Exceed",
                        'view_mode': 'form',
                        'view_id': wizard_form,
                        'view_type': 'form',
                        'res_model': 'sale.order.confirm',
                        'type': 'ir.actions.act_window',
                        'target': 'new'
                            }
            elif flag==False and flag2==True and sale.payment_term_id.id!=1:
                wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_credit_limit_v14.view_import_sale_order_due_invoice')
                return {
                        'name':"Overdue Invoices",
                        'view_mode': 'form',
                        'view_id': wizard_form,
                        'view_type': 'form',
                        'res_model': 'sale.order.confirm',
                        'type': 'ir.actions.act_window',
                        'target': 'new'
                            }
                #raise UserError(_("""Customer have some overdue invoices, please resolve first.""" ))
            elif flag==True and flag2==False and sale.payment_term_id.id!=1:
                wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_credit_limit_v14.view_import_sale_order')
                return {
                        'name':"Sale Credit Limit Exceed",
                        'view_mode': 'form',
                        'view_id': wizard_form,
                        'view_type': 'form',
                        'res_model': 'sale.order.confirm',
                        'type': 'ir.actions.act_window',
                        'target': 'new'
                            }
            else:
                popup1 = sale.action_popup()
                if popup1:
                    return popup1
                res = super(sale_order, self).action_confirm()
        else:
            popup1 = self.action_popup()
            if popup1:
                return popup1
            res = super(sale_order, self).action_confirm()
        return True

class account_move(models.Model):
    _inherit = 'account.move'

    def action_invoice_open(self):
        flag = False
        over_limit=False
        context = (self._context or {})
        part_obj = self.env['res.partner']
        if not context:
            context = {}
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time.'
        credit_limit = 0.0

        if context.get('ignore'):
            return super(account_move, self).action_invoice_open()

        sa_war=''
        for sale in self.invoice_line_ids:
            if sale.team_id:
                if sale.team_id.name == 'Website':
                    return super(account_move, self).action_invoice_open()

            if sale.move_type=='out_invoice': # and   not pos_origin:
               over_limit=sale.partner_id.over_limit
               self.env.cr.execute("select sum(amount_total) from account_move where payment_state = 'not_paid'\
                         and partner_id = %s and move_type=%s ", (sale.partner_id.id,'out_invoice',))
               res_part = self.env.cr.fetchone()
               if sale.partner_id.credit_limit and sale.partner_id.credit>0:
                   
                    credit_limit = sale.partner_id.credit_limit - sale.partner_id.credit
               if sale.partner_id.credit_limit and sale.partner_id.credit<0:
                    credit_limit=sale.partner_id.credit_limit + abs(sale.partner_id.credit)
               if sale.partner_id.credit==0.0:
                    credit_limit = sale.partner_id.credit_limit

               if sale.amount_total >credit_limit:
                    flag = True
                    sa_war='Invoice ' + ' Parnter Name ' +sale.partner_id.name

        if flag==True and over_limit==False:
            wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_credit_limit_v14.view_credit_limit_invoice')
            return {
                    'name':"Sale Credit Limit Exceed",
                    'view_mode': 'form',
                    'view_id': wizard_form,
                    'view_type': 'form',
                    'res_model': 'sale.order.confirm',
                    'type': 'ir.actions.act_window',
                    'target': 'new'
                        }
        else:
            return super(account_move, self).action_invoice_open()

