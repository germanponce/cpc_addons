# -*- coding: utf-8 -*-

{
    'name': 'Explode BOM from Production Order',
    'version': '1.0',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module returns a report that displays needed materials based on 
Production Orders final Products BOM Lists with intermediate products, obtaining total 
materials.
""",
    'depends': ['stock','mrp','sale','purchase','explode_so_bom','context_origin_action'],
    'data': [
        'views/explode_mp_bom_views.xml',
        'data/ir_exports.xml'
    ],
    'installable': True,
    'uninstall_hook':'purge_db_aux',
}
