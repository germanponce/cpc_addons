# -*- encoding: utf-8 -*-

{
    "name"      : "Purchase RO for purchase_requisition",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["purchase_requisition","product"],
    "description": """
This module enhace purchase requisition order information to add uom_po_id from product model.
""",
    "data" : [
            'views/purchase_requisition_views.xml',
        ],
    'installable': True
}
