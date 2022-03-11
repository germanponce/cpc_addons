# -*- encoding: utf-8 -*-

{
    "name"      : "Link analytic account to account.",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["analytic", "account", "purchase"],
    "description": """
This module enhace analytic account information adding account relationship.
""",
    "data" : [
            'views/analytic_account_views.xml',
        ],
    'installable': True
}
