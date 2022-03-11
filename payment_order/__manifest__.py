# -*- coding: utf-8 -*-

{
    'name': 'Payment orders',
    'version': '1.0_bd267e5c+1',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module adds Account Payment model
""",
    'depends': ['account','l10n_mx_einvoice','argil_invoice_balance_analysis','asti_eaccounting_mx_base'],
    'data': [
        'views/payment_order_views.xml',
        'views/account_invoice_supplier_balance_analysis.xml',
        'views/res_config_view.xml',
        'report/payment_order_report.xml',
        'report/payment_order_report_doc.xml',
    ],
    'installable': True,
}
