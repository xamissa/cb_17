# -*- coding: utf-8 -*-
{
    'name': "Set warehouseman [responsible] for location",
    'summary': """ This module allows to do inventory tranfer for the allowed user only""",
    'sequence': 20,
    'author': "ErpWeb",
    'category': u'Warehouse',
    'version': '17.0.0.0',
    'depends': ['stock', 'hr'],
    'data': [
             "security/security.xml",
             "views/stock_location_views.xml",
             ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license' : 'LGPL-3'
}
