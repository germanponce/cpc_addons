# -*- encoding: utf-8 -*-

{
    "name"      : "WES custimization for Repair Module",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["mrp_repair",],
    "description": """
This module enhace mrp_repair to fit WES operations.
""",
    "data" : [
            'data/stock_picking_type_data.xml',
            'views/mrp_repair_wes_base.xml',
            'views/res_partner_view.xml',
            'views/product_views.xml',
            'views/mrp_repair_views.xml',
            'views/catalogs_views.xml',
            'views/stock_picking_views.xml',
            'views/util_templates.xml',
            'views/stock_move_views.xml',
        ],
    'installable': True
}
