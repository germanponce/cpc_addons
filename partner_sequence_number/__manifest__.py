# -*- encoding: utf-8 -*-

{
    "name"      : "Sequence number for partner",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["purchase",],
    "description": """
This module enhace partner information adding Partner number automatically.
""",
    "data" : [
            'views/res_partner_views.xml',
            'data/res_partner_sequence.xml',
        ],
    'installable': True
}
