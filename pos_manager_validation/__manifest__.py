
{
    "name" : "POS Manager Validation in Odoo",
    "version" : "17.0",
    "category" : "Point of Sale",
    'summary': 'POS validate authenticate pos manager add/remove quantity pos change price pos remove order line pos remove order  pos close pos screen pos Validation pos order validate pos Manager Approval pos order validation pos double validation pos double approval',
    "description": "",
    "author": "",
    "website" : "",    
    "depends" : ['base','point_of_sale'],
    "data": [
        'views/pos_config.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_manager_validation/static/src/app/js/HeaderButton.js',
            #'pos_manager_validation/static/src/app/js/models.js',
            'pos_manager_validation/static/src/app/js/ProductScreen.js',

        ],
    },
    "auto_install": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
