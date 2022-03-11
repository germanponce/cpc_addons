# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Picking return reason',
    'version': '1.0_3ae2212d+1',
    'category': 'Stock',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module enhace picking returns from customers. It adds reason for return field and record it on generated picking.
""",
    'depends': ['stock',],
    'data': [
        'views/stock_picking_views.xml',
        'wizard/stock_picking_return_views.xml',
    ],
    'installable': True,
}
