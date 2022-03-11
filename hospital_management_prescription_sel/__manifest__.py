# -*- coding: utf-8 -*-

{
    'name': 'Hospital Management. Prescription Report Select',
    'version': '1.0',
    'category': 'Industries',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module enhace hospital_management for choose Prescription Report Size.
Additionally, It rewrites create invoice from prescription Wizard
""",
    'depends': ['hospital_management',],
    'data': [
#        'views/VISTA_1.xml',
        'wizard/prescription_select.xml',
#        'data/DATOS_1.xml',
        'report/prescription_reports.xml',
        'report/prescription_reports_doc.xml'
    ],
    'installable': True,
    'post_init_hook':'set_post_init',
    'uninstall_hook':'reset_deps',
}
