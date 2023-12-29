from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp

class ResUsers(models.Model):
	_inherit = 'res.users'

	pos_security_pin = fields.Char(string='Security PIN', size=32, help='A Security PIN used to protect sensible functionality in the Point of Sale')

	@api.constrains('pos_security_pin')
	def _check_pin(self):
		if self.pos_security_pin and not self.pos_security_pin.isdigit():
			raise UserError(_("Security PIN can only contain digits"))

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_users(self):
        result = super()._loader_params_res_users()
        result['search_params']['fields'].append('pos_security_pin')
        return result




class PosConfigInherit(models.Model):
	_inherit = 'pos.config'

	pos_user_id = fields.Many2one('res.users',string='Manager')
	pos_secondary_user_id = fields.Many2one('res.users',string=' secondary Manager')
	pos_close_pos = fields.Boolean(string='Closing Of POS')
	pos_order_delete = fields.Boolean(string='Order Deletion')
	pos_order_line_delete = fields.Boolean(string='Order Line Deletion')
	pos_qty_detail = fields.Boolean(string='Add/Remove Quantity')
	pos_discount_app = fields.Boolean(string='Apply Discount')
	pos_payment_perm = fields.Boolean(string='Payment')
	pos_price_change = fields.Boolean(string='Price Change')
	pos_one_time_valid = fields.Boolean(string='One Time Password for an Order')
	pos_set_max_discount = fields.Integer(string="Set Maximum Discount(in %)")

class ResConfigSetting(models.TransientModel):
	_inherit = 'res.config.settings'

	user_id = fields.Many2one('res.users',string='Manager',compute='_compute_pos_user_id',related='pos_config_id.pos_user_id',readonly=False)
	secondary_user_id = fields.Many2one('res.users',string=' secondary Manager',related='pos_config_id.pos_secondary_user_id',readonly=False)
	close_pos = fields.Boolean(related='pos_config_id.pos_close_pos' ,string='Closing Of POS',readonly=False)
	order_delete = fields.Boolean(related='pos_config_id.pos_order_delete' ,string='Order Deletion',readonly=False)
	order_line_delete = fields.Boolean(related='pos_config_id.pos_order_line_delete' ,string='Order Line Deletion',readonly=False)
	qty_detail = fields.Boolean(related='pos_config_id.pos_qty_detail' ,string='Add/Remove Quantity',readonly=False)
	discount_app = fields.Boolean(related='pos_config_id.pos_discount_app' ,string='Apply Discount',readonly=False)
	payment_perm = fields.Boolean(related='pos_config_id.pos_payment_perm' ,string='Payment',readonly=False)
	price_change = fields.Boolean(related='pos_config_id.pos_price_change' ,string='Price Change',readonly=False)
	one_time_valid = fields.Boolean(related='pos_config_id.pos_one_time_valid' ,string='One Time Password for an Order',readonly=False)
	set_max_discount = fields.Integer(string="Set Maximum Discount(in %)",related='pos_config_id.pos_set_max_discount',readonly=False)