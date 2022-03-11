# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Sale Order Auto Tracking',
    'version': '1.0',
    'category': 'Stock',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module keeps tracking confirmed sale orders on setting days lapse if it is not delivered by mailing customer and vendor
""",
    'depends': ['sale','mail'],
    'data': [
        'views/sale_state_config_views.xml',
        'data/data.xml',
    ],
    'installable': True,
    'post_init_hook':'set_defaults',
}
