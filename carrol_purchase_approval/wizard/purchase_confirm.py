##############################################################################
#
#    ERP WEB
#
##############################################################################
from odoo.tools.translate import _
from odoo.osv import osv
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class purchase_order_confirm(models.TransientModel):
    _name = "purchase.order.confirm"
    _description = "Purchase Order Confirm"

    reject_note = fields.Text('Reject Note')

    # validate
    def confim_orders(self):
        purchase_approval_obj = self.env['purchase.approval']
        purchase_obj = self.env['purchase.order']
        purchase_ids = purchase_obj.browse(self._context.get('active_ids'))

        validate_approval = purchase_approval_obj.search([('name','=', 'validate_purchase')], limit=1)
        if validate_approval:
            purchase_ids._create_approvals(validate_approval)
        else:
            raise ValidationError(_('Please configure approval properly!'))
        if purchase_ids:
            if self.env.uid in purchase_ids.approval_ids.filtered(lambda x: x.status == 'none' and x.approval_data_name == 'validate_purchase').mapped('required_user_ids').ids:
                purchase_ids.validate_order()
        return True

    def approval_request(self):
        purchase_obj = self.env['purchase.order']
        purchase_approval_obj = self.env['purchase.approval']
        purchase_ids = purchase_obj.browse(self._context.get('active_ids'))
        
        validate_approval = purchase_approval_obj.search([('name','=', 'validate_purchase')], limit=1)
        if validate_approval:
            purchase_ids._create_approvals(validate_approval)
            purchase_ids.state = 'purchase_to_validate'
        else:
            raise ValidationError(_('Please configure approval properly!'))

        message = ("Approval Request Send by "+str(self.env.user.name))
        purchase_ids.message_post(body=message)

        line = purchase_ids.approval_ids.filtered(lambda x: x.status == 'none' and x.approval_data_name == 'validate_purchase')
        if purchase_ids.approval_ids:
            for user in purchase_ids.approval_ids.required_user_ids:
                purchase_ids.activity_schedule(
                    'carrol_purchase_approval.mail_activity_type_purchase_approval',
                    user_id=user.id or SUPERUSER_ID,
                    note=_("Validation Request")
                )
        return True

    def reject_approval_request(self):
        purchase_obj = self.env['purchase.order']
        purchase_ids = purchase_obj.browse(self._context.get('active_ids'))
        
        message = ("Approval Request rejected by "+str(self.env.user.name) +' Rejection Message:' +str(self.reject_note))
        purchase_ids.message_post(body=message)

        line = purchase_ids.approval_ids.filtered(lambda x: self.env.uid in x.required_user_ids.ids and x.status == 'none' and x.approval_data_name in ['validate_purchase','approve_purchase'])
        if line:
            line.write({'status': 'rejected', 'user_id': self.env.uid, 'approval_date': fields.Datetime.now()})

        purchase_ids.state='draft'
        return True
