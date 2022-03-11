# -*- encoding: utf-8 -*-

{
    "name"      : "Procurement Wizard Per Warehouse",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["purchase_requisition",],
    "description": """
This module enhace procurement Wizard to add warehouse domain.
""",
    "data" : [
            'wizard/procurement_orderpoint_compute.xml',
        ],
    'installable': True
}
