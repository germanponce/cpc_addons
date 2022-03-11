# -*- coding: utf-8 -*-

{
    'name': 'Raloy customizations',
    'version': '1.0_d88437df+1',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
Multiple customizations to fit Raloy processes.

*Disable sequence validation on setting next step minor than current progress on print checks.
""",
    'depends': [
        'account',
        'account_check_printing',
        'account_supplier_invoice_payment_order'
    ],
    'data': [
#        'views/VISTA_1.xml',
#        'data/DATOS_1.xml',
#        'report/report_stockpicking_operations.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
#    'post_init_hook':'set_defaults',
}
