# -*- coding: utf-8 -*-

{
    'name': 'Explode BOM from Sale Order',
    'version': '1.0',
    'category': 'Purchase',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module returns a report that projecs future purchases based on 
Sale Orders and BOM Lists with intermediate products, obtaining total 
materials.
""",
    'depends': ['stock','mrp','sale','purchase'],
    'data': [
        'wizard/explode_so_bom_select.xml',
        'views/explode_so_bom_views.xml',
        'views/res_config_views.xml',
        'views/product_template_views.xml',
        'data/ir_exports.xml'
    ],
    'installable': True,
    'post_init_hook':'set_defaults',
    'uninstall_hook':'purge_db_aux',
}
