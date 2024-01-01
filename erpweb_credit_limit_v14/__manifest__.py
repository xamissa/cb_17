# -*- coding: utf-8 -*-
{
    'name': 'Credit Limit',
    'version': '1.0.1',
    'category': 'Accounting',
    'sequence': 6,
    'summary': 'Warning MSG credit limit',
    'description': """
     All custom functionality requested by Uno
    """,
    'author': 'Erpweb',
    'images': [],
    'depends': ['account','sale_management','stock','account_accountant', ],
    # TODO: 'takealot_odoo', 'odoo_magento2_ept'],
    'data': [
        'sale_view.xml',
        'wizard/sale_confim.xml',
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'wizard/sale_credit_limit.xml',
    ],
    'demo': [],
    'test': [],
    'application': True,
    'qweb': [],
    'auto_install': False,
}
