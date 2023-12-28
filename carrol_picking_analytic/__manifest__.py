# -*- coding: utf-8 -*-
{
    'name': 'Analytic Account on Stock Picking with Analytic Tags in Odoo',
    'version': '17.0.0.1',
    'category': 'Warehouse',
    'summary': 'Set Analytic account and analytic tag on Stock Picking',
    'description': """
    """,
    'author': '',
    'depends': ['base','sale_management','stock','analytic',"stock_account",'purchase'],
    'data': [
                "views/stock_move_views.xml"
            ],
    'qweb': [ ],
    'demo': [ ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

