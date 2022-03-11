# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Automatic Orderpoint',
    'version': '1.0_6def6244+1',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module calculates maximun and minimum based on average consumption.
""",
    'depends': [
        'stock',
        'product',
    ],
    'data': [
        'views/orderpoint_views.xml',
        'views/explode_lvl_bom_views.xml',
        'views/stock_move_views.xml',
        'views/purchase_category_views.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
