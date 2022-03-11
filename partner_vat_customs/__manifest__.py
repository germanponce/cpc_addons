# -*- encoding: utf-8 -*-

{
    "name"      : "VAT field customizations for partner",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["mail", "purchase"],
    "description": """
This module enhace partner information adding VAT field requiered and unique.
""",
    "data" : [
            'views/res_partner_views.xml',
        ],
    'installable': True
}
