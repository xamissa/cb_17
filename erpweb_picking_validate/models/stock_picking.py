from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    virtual_location = fields.Boolean('Virtual Location', default=False, store=True)  

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        user_grp = self.env.user.has_group( "erpweb_picking_validate.group_picking_validate")
        print("DESTINATIONNNNNNNNNNNNNNNNNNNN", self.location_dest_id)
        if user_grp and self.env.user.id in self.location_dest_id.allowed_users.ids and self.location_dest_id.virtual_location:
            return super(StockPicking, self).button_validate()
        else :
            raise UserError(_("""You cannot validate transfer for virtual location!!""" ))
        return super(StockPicking, self).button_validate()


