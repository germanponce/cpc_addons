# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Mail Delivery Notification',
    'version': '1.0',
    'category': 'Stock',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module enhace delivery by mailing customer and vendor when order is shipped
""",
    'depends': ['delivery','mail'],
    'data': [
        'views/delivery_mail_config_views.xml',
        'data/mail_template.xml',
    ],
    'installable': True,
    'post_init_hook':'set_defaults',
}
