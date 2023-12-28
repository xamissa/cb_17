{
    'name' : 'Carrolboyes Custom Extra',
    'version' : '17.0',
    'summary': '',
    'sequence': 15,
    'description': """ Add Extra Customization """,
    'category': 'Stock',
    'website': '',
    'depends' : ['sale_stock','sale','stock_account','product'],
    'data': [
        'views/stock_view.xml',
        'views/activity_view.xml',
        'wizard/sale_confirm_popup.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license' : 'LGPL-3'
}
