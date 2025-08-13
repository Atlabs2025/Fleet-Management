# -*- coding: utf-8 -*-
{
    'name': 'Vehicle Stock Book',
    'version': '18.0.1.0.0',
    'category': 'Vehicle Stock',
    'summary': 'Stock of the vehicles',
    'description': 'stock book',
    'depends': [
        'base','stock', 'fleet'
    ],
'data': [
    # 'security/car_user_security.xml',
    'security/ir.model.access.csv',
    # 'data/sequence.xml',
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