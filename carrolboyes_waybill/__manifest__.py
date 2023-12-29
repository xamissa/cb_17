# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Carrolboyes Waybill',
    'category': 'Hidden/Tools',
    'summary': 'Integrates Odoo with WhatsApp to use WhatsApp messaging service',
    'version': '1.0',
    'description': """This module integrates Odoo with WhatsApp to use WhatsApp messaging service""",
    'depends': ['stock','utm','base','delivery'],
    'data': [
            'security/ir.model.access.csv',
            'data/waybill_data.xml',
            'views/postcode.xml',
            'views/ir_sequence.xml',
    ],
    'license': 'OEEL-1',
    'application': True,
    'installable': True,
}
