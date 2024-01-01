# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Carrolboyes Sale Stock',
    'category': 'Inventory/Inventory',
    'summary': 'Carrolboyes Sale Stock',
    'version': '1.0',
    'depends': ['sale_stock','sale_management', 'sales_team','account_accountant', 'crm'],
    'data': [
            'security/stock_security.xml',
            'views/crm_team_views.xml',
            'views/sale_order_views.xml',
            'views/product_views.xml',
    ],
    'license': 'OEEL-1',
    'application': True,
    'installable': True,
    'module_type': 'official'
}
