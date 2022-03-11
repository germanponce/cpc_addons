# -*- coding: utf-8 -*-

{
    "name" : "Interactive Invoice Balance Analysis - Multi",
    "version" : "2.1.1",
    "author" : 'Argil Consulting',
    "summary": "Interactive Invoice Balance Analysis with 30 or 7 days ranges",
    "description" : """
This module creates new AR and AP views.

Odoo Version: 10.0

""",
    'maintainer': 'Argil Consulting',
    'website': 'http://www.argil.mx',
    "category": 'Accounting & Finance',
    "images" : [],
    "depends" : ["account","argil_invoice_balance_analysis"],
    "data" : [
#              'views/account_invoice_supplier_balance_analysis.xml',
              'views/res_config_view.xml',
              'wizard/argil_invoice_analysis_wizard.xml',
    ],
    "test" : [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

