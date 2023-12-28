# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    def _prepare_mail_values(self, name, client, ticket):
        res = super(PosOrderInherit, self)._prepare_mail_values(name, client, ticket)
        if self.env.company.pos_email:
            res.update({'email_from': self.env.company.pos_email}) 
        return res


class Company(models.Model):
    _inherit = "res.company"

    pos_email = fields.Char('PoS Email')
