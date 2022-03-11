# -*- coding: utf-8 -*-

{
    "name" : "Supplier Invoice Payment Order",
    "version" : "2.1.1_bd267e5c+1",
    "author" : 'Argil Consulting',
    "summary": "Supplier Invoice Payment Order",
    "description" : """
This module adds a wizard to get Payment Order Report for Supplier Invoices

It superseeds supplier_journal_id for replaces functionality.

Odoo Version: 10.0

""",
    'maintainer': 'Argil Consulting',
    'website': 'http://www.argil.mx',
    "category": 'Accounting & Finance',
    "images" : [],
    "depends" : ["account","l10n_mx_einvoice", "argil_invoice_balance_analysis_multi","payment_order","account_supplier_invoice_payment_order_extend"],
    "data" : [
              'views/partner_view.xml',
              'views/res_bank_view.xml',
              'data/supplier_payment_rpt_seq.xml',
              'wizard/account_invoice_balance_view.xml',
    ],
    "test" : [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

