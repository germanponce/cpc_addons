# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Análisis para Llamadas',
    'version': '1.0',
    'category': 'crm',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
Este módulo añade una vista pivote para análisis de las llamadas.
""",
    'depends': ['isep_custom','hr'],
    'data': [
        'views/llamadas_isep_report_views.xml',
    ],
    'installable': False,
}
