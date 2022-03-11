# -*- encoding: utf-8 -*-

{
    "name"      : "Log for Purchase Order on price change (From Done to Draft)",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["mail", "purchase"],
    "description": """
This module enhace purchase order information to add a price changes log when this comes to draft from done states.
""",
    "data" : [
            'data/purchase_order_log_data.xml',
            'views/purchase_views.xml',
        ],
    'installable': True
}
