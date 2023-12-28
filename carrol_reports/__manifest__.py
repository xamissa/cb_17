# -*- coding: utf-8 -*-

{
    'name': "Carrolboyes Reports Customization",
    'summary': "Carrolboyes Report",
    'description': """Carrolboyes Reports Customizations.""",
    'category': 'Inventory/Inventory',
    'version': '17.0',
    'depends': ['sale_stock','account', 'delivery'],
    'data': [
             'security/ir.model.access.csv',
             'views/sale_view.xml',
             'views/stock_picking.xml',
             'views/freight_company_view.xml',
             'views/magento_gift_view.xml',
             'views/report_picking_inherit.xml',
             'views/report_invoice_inherit.xml',
             'views/report_invoice_picking.xml',
             'views/report_delivery_inherit.xml',
             'views/report_sale_order.xml',
             'views/gift_receipt.xml',
    ],
    'qweb': [
     ],
    'installable': True,
    'application': True,
    'license' : 'LGPL-3'
}
