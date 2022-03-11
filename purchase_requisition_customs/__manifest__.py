# -*- encoding: utf-8 -*-

{
    "name"      : "Purchase Requisition enhacements based on CPC process",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["purchase_requisition","product","analytic"],
    "description": """
This module enhace purchase requisition to fit CPC process: Required analytic account on requisition lines when 
product is different than 'Product' type and log changes when 1 Step purchase changes.
""",
    "data" : [
            'views/purchase_requisition_views.xml',
        ],
    'installable': True
}
