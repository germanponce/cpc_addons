# -*- encoding: utf-8 -*-

{
    "name"      : "Log for product supplier info",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["mail", "product"],
    "description": """
This module enhace product supplier information to add a price changes log.
""",
    "data" : [
            'data/product_log_data.xml',
            'views/product_views.xml',
        ],
    'installable': True
}
