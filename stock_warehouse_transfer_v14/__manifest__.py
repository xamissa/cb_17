# -*- coding: utf-8 -*-


{
    'name': 'Stock Warehouse Transfer',
    'version': '17.0',
    'license': 'AGPL-3',
    'author': 'erpweb',
    'website': 'http://www.erpweb.co.zu',
    'category': 'Purchase',
    'complexity': 'normal',
    'summary': 'Create a transfer of products between 2 warehouses',
    'depends': [
        'stock','sales_team'
    ],
    'data': [
        'views/stock_warehouse_transfer.xml',
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/report_picking.xml'
    ],
}
