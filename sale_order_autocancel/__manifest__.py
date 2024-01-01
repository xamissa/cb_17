# -*- coding: utf-8 -*-
{
    'name': 'Sale Order - Cancel after expire date.',
    'category': 'Accounting/Sales',
    'description': """
Sale Order - Cancel after expire date.=======================
Allows auto cancellation of sale order that stay in quotation state after a time (draft and sent state).
""",
    'version': '17.0',
    'depends': ['sale_management'],
    'data': [
           'views/ir_cron.xml',
           'views/sale.xml',
    ],
    'license': 'OEEL-1',
    'application': True,
    'installable': True,
    'module_type': 'official'
}
