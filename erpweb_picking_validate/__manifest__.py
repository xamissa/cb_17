# -*- coding: utf-8 -*-
{
    'name': "Carrolboyes Transfer Validate",
    'summary': "Carrolboyes Transfer Validate",
    'description': """ If user have access and allowed user on location then validate the transfer """,
    'category': 'stock',
    'version': '17.0',
    'depends': ['stock'],
    'data': [
        'security/stock_security.xml',
        'views/stock_picking.xml',
    ],
    'qweb': [
     ],
    'installable': True,
    'application': True,
    'license' : 'LGPL-3'
}
