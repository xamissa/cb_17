{
    "name": "POS Analytic Config",
    "summary": "Use analytic account defined on POS configuration for POS Journal Items",
    'description': """
        Use analytic account defined on POS configuration for POS Journal Items
    """,
    "website": "",
    "category": "Point Of Sale, Accounting",
    "version": "17.0",
    "depends": ["point_of_sale"],
    "data": [
        "views/pos_config_view.xml",
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}