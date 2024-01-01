# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Restrict Users on Stock picking type',
    'category': 'stock',
    'summary': 'Restrict users to picking types',
    'version': '1.0',
    'description': """""",
    'depends': [
        'stock','purchase',
    ],
    'data': [
            'security/stock_security.xml',
            'views/stock_picking_type_views.xml',
    ],
    'license': 'OEEL-1',
    'application': True,
    'installable': True,
}
