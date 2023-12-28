import datetime
from odoo import fields, models, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class PosHrEmployeeInherit(models.Model):
   _inherit = 'hr.employee'

   emp_registartion_number = fields.Integer(string="Registration Number of an employee",groups="hr.group_hr_user")

   def get_emp_registartion_number(self):
      print("nnnnnnnnnnnnnnnnnnnnn",self)
      if self:
         emp = self.env['hr.employee'].sudo().search([('id', '=',self.id)])
         result= emp.emp_registartion_number
         return result
      return 
