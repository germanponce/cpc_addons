# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Custom Views for CPC',
    'version': '1.0',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
A collection of custom views for CPC workflow
""",
    'depends': ['account','sf_link_elemental'],
    'data': [
        'views/invoice_mgr_journal.xml',
        'report/report_purchaserequisition.xml',
    ],
    'installable': True,
}
