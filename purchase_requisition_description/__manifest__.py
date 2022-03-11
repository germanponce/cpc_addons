# -*- encoding: utf-8 -*-

{
    "name"      : "Description field for purchase_requisition",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["purchase_requisition",],
    "description": """
This module enhace purchase requisition order information to add a description.
""",
    "data" : [
            'views/purchase_requisition_views.xml',
        ],
    'installable': True
}
