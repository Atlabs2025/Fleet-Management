# -*- coding: utf-8 -*-
{
    'name': 'Project Task',
    'version': '18.0.1.0.0',
    'category': 'Vehicle Stock',
    'summary': 'Stock of the vehicles',
    'description': 'stock book',
    'depends': [
        'stock', 'fleet'
    ],
'data': [
    'security/ir.model.access.csv',
    # 'views/vehicle_stock_book.xml',
    'views/product_template.xml',
    # 'views/menu.xml',
],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}