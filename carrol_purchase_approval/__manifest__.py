{
    'name' : 'Carrol Boys: Purchase Approval',
    'version' : '14.0',
    'summary': '',
    'sequence': 1,
    'description': """ Purchase Approval """,
    'category': 'Purchase',
    'website': '',
    'depends' : ['purchase'],
    'data': [
        'data/purchase_activity.xml',
        'security/ir.model.access.csv',
        'views/approval_menu.xml',
        'views/purchase_view.xml',
        'wizard/purchase_confirm.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license' : 'LGPL-3'
}
