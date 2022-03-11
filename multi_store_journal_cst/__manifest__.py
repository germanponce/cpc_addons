# -*- encoding: utf-8 -*-

{
    "name"      : "Journal on MultiStore.",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["account", "purchase_requisition", "base_multi_store",],
    "description": """
This module enhace product requsition process adding fiscal position relationship to store and related automations.
""",
    "data" : [
            'views/res_store_view.xml',
            'views/purchase_views.xml',
            'views/account_invoice_view.xml',
        ],
    'installable': True
}
