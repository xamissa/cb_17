from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Picking(models.Model):
	_inherit = "stock.picking"

	@api.depends('state')
	def _get_invoiced(self):
		for order in self:
			invoice_ids = self.env['account.move'].search([('picking_id','=',order.id)])
			order.invoice_count = len(invoice_ids)
	invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced')
	
	def button_view_invoice(self):
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		work_order_id = self.env['account.move'].search([('picking_id', '=', self.id)])
		inv_ids = []
		action = self.env.ref('account.action_move_out_invoice_type').read()[0]
		context = {'default_move_type': work_order_id[0].move_type,}
		action['domain'] = [('id', 'in', work_order_id.ids)]
		action['context'] = context
		return action

	
	def _action_done(self):
		action = super(Picking, self)._action_done()
		res_config = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
		if len(self) == 1:
			for picking in self:
				if picking.state == 'done'  :
					if picking.picking_type_id.code == 'outgoing':
						if picking.origin:
							pass
						else:
							picking.update({'origin': self._context.get('default_origin')})    
						inv_obj = self.env['account.move']
						invoice_lines =[]
						invoice_vals = []
						sale_order_line_obj = self.env['account.move.line']
						sale_order  =  self.env['sale.order'].search([('name', '=',picking.origin)])
						journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
						if not journal:
							raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (picking.company_id.name, picking.company_id.id))
						if sale_order:
							vals  = {
								'invoice_origin': picking.origin,
								'picking_id':picking.id,
								'move_type': 'out_invoice',
								'ref': sale_order.client_order_ref or '',
								'sale_id':sale_order.id,
								'journal_id': journal.id,  
								'partner_id': sale_order.partner_invoice_id.id,
								'currency_id': sale_order.pricelist_id.currency_id.id,
								'invoice_payment_term_id': sale_order.payment_term_id.id,
								'fiscal_position_id': sale_order.fiscal_position_id.id or sale_order.partner_id.property_account_position_id.id,
								'team_id': sale_order.team_id.id,
								'invoice_date' : fields.Datetime.now().date(),
                                'invoice_user_id' : sale_order.user_id and sale_order.user_id.id,
                                'gift_voucher_ids' : [(4, x) for x in sale_order.gift_voucher_ids.ids],
                                #'magento_payment_method_id': sale_order.magento_payment_method_id and sale_order.magento_payment_method_id.id,
                                'currency_id': sale_order.currency_id.id,

							}
							
							model_id = self.env['ir.model'].search([('model','=','sale.order')])
							is_avail_fields = self.env['ir.model.fields'].search([('name','=','l10n_in_company_country_code'),('model_id','=',model_id.id)])
							if is_avail_fields:
							
								if sale_order.l10n_in_company_country_code == 'IN':
									vals['l10n_in_reseller_partner_id'] = sale_order.l10n_in_reseller_partner_id.id
									if sale_order.l10n_in_journal_id:
										vals['journal_id'] = sale_order.l10n_in_journal_id.id
										vals['l10n_in_gst_treatment'] = sale_order.l10n_in_gst_treatment
							
							if not sale_order.partner_id.property_payment_term_id: #added by 15/2
								sale_order.partner_id.property_payment_term_id = sale_order.payment_term_id.id
							invoice = inv_obj.create(vals)
							
							
							for so_line in  sale_order.order_line :
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
													#'analytic_account_id': so_line.analytic_account_id.id,
													'analytic_distribution': {so_line.analytic_account_id.id: 100},
													'display_type': so_line.display_type or 'product',
													'tax_ids': [(6, 0, so_line.tax_id.ids)],
													'discount': so_line.discount,
													'move_id':invoice.id,
													'price_unit': so_line.price_unit,
													'sale_line_ids': [(4, so_line.id)],
													'currency_id': so_line.currency_id.id,
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
	
										route = self.env['stock.route'].search([('name','=','Dropship')])
										if self._context.get('flag') == True and route.id in so_line.product_id.route_ids.ids:
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
															#'analytic_account_id': so_line.analytic_account_id.id,
															'analytic_distribution': {so_line.analytic_account_id.id: 100},
															'display_type': so_line.display_type or 'product',
															'tax_ids': [(6, 0, so_line.tax_id.ids)],
															'discount': so_line.discount,
															'move_id':invoice.id,
															'price_unit': so_line.price_unit,
															'sale_line_ids': [(4, so_line.id)],
															'currency_id': sale.currency_id.id,
															}
													invoice_vals.append((0,0,inv_line))

													so_line.write({'qty_to_invoice':so_line.product_uom_qty})
											else:
												inv_line = {
														'name': so_line.name,
														'product_id': so_line.product_id.id,
														'product_uom_id': so_line.product_id.uom_id.id,
														'quantity': so_line.product_uom_qty,
														'account_id': account.id, #4195 currently not available in system,
														#'analytic_account_id': so_line.analytic_account_id.id,
														'analytic_distribution': {so_line.analytic_account_id.id: 100},
														'display_type': so_line.display_type or 'product',
														'tax_ids': [(6, 0, so_line.tax_id.ids)],
														'discount': so_line.discount,
														'move_id':invoice.id,
														'price_unit': so_line.price_unit,
														'sale_line_ids': [(4, so_line.id)],
														'currency_id': so_line.currency_id.id,
														}
											 
												invoice_vals.append((0,0,inv_line))
												
												so_line.write({'qty_to_invoice':so_line.product_uom_qty})
							invoice.write({
								'invoice_line_ids' : invoice_vals
							})
							if invoice:
								if invoice.invoice_line_ids:
									invoice.action_post()
								if invoice.partner_id.team_id.id in (5,35,14):
									template = self.env.ref('account.email_template_edi_invoice', False)
									if template:
										#self.env['mail.template'].sudo().browse(template.id).send_mail(invoice.id, force_send=True)
										invoice.with_context(force_send=True,model_description='Invoice').message_post_with_template(template.id)
			return action
