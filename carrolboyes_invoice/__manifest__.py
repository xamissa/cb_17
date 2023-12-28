# -*- coding: utf-8 -*-

{
    'name': "Carrolboyes Sale invoice",
    'summary': "Carrolboyes Sale invoice",
    'description': """Carrolboyes Sale Stock.""",
    'category': 'Inventory/Inventory',
    'version': '17.0.1.0',
    'depends': ['account','sale_stock','sale_management', 'sales_team'],
    'data': [
                'security/ir.model.access.csv',
				'views/account_move.xml',
				'views/stock_picking.xml',
				'views/res_config.xml',  
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
