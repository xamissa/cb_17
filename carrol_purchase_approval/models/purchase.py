# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrderApproval(models.Model):
    _name = "purchase.order.approval"
    _description = 'Purchase Order Approval'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order',
        ondelete='cascade', required=True)
    user_id = fields.Many2one('res.users', 'Approved by')
    required_user_ids = fields.Many2many('res.users', string='Requested Users')
    status = fields.Selection([
        ('none', 'Not Yet'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], string='Status',
        default='none', required=True)
    approval_date = fields.Datetime('Approval Date')
    approval_data_id = fields.Many2one('purchase.approval', 'Technical field')
    approval_data_name = fields.Selection(related='approval_data_id.name')

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_approved = fields.Boolean('Is Approved?', copy=False)
    to_approve = fields.Boolean('To Approve', copy=False)
    rejected_approval = fields.Boolean('Rejected', copy=False)
    approval_ids = fields.One2many('purchase.order.approval', 'purchase_order_id', 'Approvals', help='Approvals')
    state = fields.Selection(selection_add=[('purchase_to_validate', 'To Validate'), ('purchase_to_final_approval', 'To Final Approval')])

    def _create_approvals(self, approvals):
        for approval in approvals:
            user_ids = approval.user_ids.ids
            if user_ids:
                self.env['purchase.order.approval'].create({
                    'purchase_order_id': self.id,
                    'required_user_ids': [(6, 0, user_ids)],
                    'approval_data_id': approval.id,
                })
        self.to_approve = True

    def write(self, vals):
        if self.state == 'draft' and not vals.get('state'):
            approval = self.env['purchase.approval'].sudo().search([('name','=','create_purchase')],limit=1)
            user_ids = approval.user_ids.ids
            user_ids.append(1)
            if self.env.uid not in user_ids:
                raise UserError(_('You are not allow to create/edit budget OR Approval list not configured!'))
        if self.state in ['purchase_to_validate','purchase_to_final_approval']:
            print ('===>>',vals)
            # if not vals.get('state'):
            #     raise ValidationError(_('You are not allowed to Modify Order!'))
        res = super(PurchaseOrder, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        user_ids = []
        approval = self.env['purchase.approval'].sudo().search([('name','=','create_purchase')],limit=1)
        if approval:
           user_ids = approval.user_ids.ids
        user_ids.append(1)
        if self.env.uid not in user_ids:
            raise UserError(_('You are not allow to create Purchase Order OR Approval list not configured!'))
        return super(PurchaseOrder, self).create(vals)

    def final_approval(self):
        line = self.approval_ids.filtered(lambda x: self.env.uid in x.required_user_ids.ids and x.status == 'none' and x.approval_data_name == 'approve_purchase')
        if line:
            line.write({'status': 'approved', 'user_id': self.env.uid, 'approval_date': fields.Datetime.now()})
            message = ("Purchase order Final Approved by "+str(self.env.user.name))
            self.message_post(body=message)
            self.sudo().button_confirm()
            self.sudo().button_done()
            return True
        else:
            raise ValidationError(_('You are not allowed to Approves!'))

    def validate_order(self):
        line = self.approval_ids.filtered(lambda x: self.env.uid in x.required_user_ids.ids and x.status == 'none' and x.approval_data_name == 'validate_purchase')
        if line:
            line.write({'status': 'approved', 'user_id': self.env.uid, 'approval_date': fields.Datetime.now()})
            self.state = 'purchase_to_final_approval'
            message = ("Purchase order Validated by "+str(self.env.user.name))
            self.message_post(body=message)
            
            # send for final approval request
            validate_approval = self.env['purchase.approval'].search([('name','=', 'approve_purchase')], limit=1)
            if validate_approval:
                self._create_approvals(validate_approval)
                for user in validate_approval.user_ids:
                    self.activity_schedule(
                        'carrol_purchase_approval.mail_activity_type_purchase_approval',
                        user_id=user.id or SUPERUSER_ID,
                        note=_("Final Approval Request")
                    )
        else:
            raise ValidationError(_('You are not allowed to Validate!'))

    def button_confirm(self):
        for order in self:
            # if order.state not in ['draft', 'sent']:
            #     continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.company.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def reject_order(self):
        line = self.approval_ids.filtered(lambda x: self.env.uid in x.required_user_ids.ids and x.status == 'none' and x.approval_data_name in ['validate_purchase','approve_purchase'])
        if not line:
            raise ValidationError(_('You are not allowed to Reject!'))

        wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_purchase_approval.view_send_rejection')
        return {
                'name':"Reject Approval Request",
                'view_mode': 'form',
                'view_id': wizard_form,
                'view_type': 'form',
                'res_model': 'purchase.order.confirm',
                'type': 'ir.actions.act_window',
                'target': 'new'
                }

    def send_for_approval(self):
        purchase_approval_obj = self.env['purchase.approval']
        for order in self:
            if not order.order_line:
                raise ValidationError(_('Please add order lines to Send for Validation!'))
            order.approval_ids.filtered(lambda x: x.status == 'none').unlink()

            validate_approval = purchase_approval_obj.search([('name','=', 'validate_purchase')], limit=1)

            if self.env.uid in validate_approval.user_ids.ids:
                wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_purchase_approval.view_confirm_purchase_order')
                return {
                        'name':"Reject Approval Request",
                        'view_mode': 'form',
                        'view_id': wizard_form,
                        'view_type': 'form',
                        'res_model': 'purchase.order.confirm',
                        'type': 'ir.actions.act_window',
                        'target': 'new'
                        }
            else:
                wizard_form = self.env['ir.model.data']._xmlid_to_res_id('erpweb_purchase_approval.view_send_for_approval')
                return {
                        'name':"Send Validation Request.",
                        'view_mode': 'form',
                        'view_id': wizard_form,
                        'view_type': 'form',
                        'res_model': 'purchase.order.confirm',
                        'type': 'ir.actions.act_window',
                        'target': 'new'
                        }
