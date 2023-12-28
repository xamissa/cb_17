{
    "name": "POS Item Count",
    "summary": """ POS Item Count""",
    "images": [],
    "version": "17.0",
    "depends": ["base", "point_of_sale",],
    "data": [
        'views/hr_employee.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'erpweb_pos_item_count/static/src/app/**/*',            
        ],
    },
    "auto_install": False,
    "installable": True,
}
