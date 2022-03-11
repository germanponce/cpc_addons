# -*- coding: utf-8 -*-

{
    "name" : "Interactive Invoice Balance Analysis - Supplier Report",
    "version" : "2.1.1",
    "author" : 'Argil',
    "summary": "Interactive Invoice Balance Analysis with report for supplier Payment order",
    "description" : """
This module adds a report for Supplier

Odoo Version: 10.0

""",
    'maintainer': 'Argil Consulting',
    'website': 'http://www.argil.mx',
    "category": 'Accounting & Finance',
    "images" : [],
    "depends" : ["account","l10n_mx_einvoice", "argil_invoice_balance_analysis_multi"],
    "data" : [
#              'views/account_invoice_supplier_balance_analysis.xml',
              'views/partner_view.xml',
              'views/res_bank_view.xml',
              'data/supplier_payment_rpt_seq.xml',
              'report/supplier_payment_report.xml',
              'report/supplier_payment_report_doc.xml',
    ],
    "test" : [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

