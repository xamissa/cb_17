
{
    "name" : "POS Price Change Report",
    "version" : "17.0",
    "category" : "Point of Sale",
    'summary': 'POS manager change price, Add it details on the report like session, order no, product, qty, unit price, updated price and date&time',
    "description": "",
    "author": "ERPWEB",
    "website" : "",    
    "depends" : ['base','point_of_sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_price_change_report.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_price_change_report/static/src/app/models.js',
            'pos_price_change_report/static/src/app/pos.xml',

            
        ],
    },
    "auto_install": False,
    "installable": True,
}
