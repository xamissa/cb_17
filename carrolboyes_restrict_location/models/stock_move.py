# -*- coding: utf-8 -*-

from odoo import api, models,fields, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self,cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        uid = self.env.user.id
        if self:
            for record in self:
                srcl = record.location_id
                dstl = record.location_dest_id
                if (uid not in srcl.allowed_users.ids) and (uid not in dstl.allowed_users.ids):
                    raise ValidationError(_('You are not allowed to do transfer'))
                else:
                    return res
        return res
