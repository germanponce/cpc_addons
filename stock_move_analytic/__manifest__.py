# -*- coding: utf-8 -*-
{
    'name': 'Stock Move Analytic',
    'author': 'ERP Ukraine, Argil Consulting S.A. & German Ponce Dominguez',
    'website': 'https://argil.mx',
    'category': 'Corona',
    'depends': ['stock', 'stock_account'],
    'version': '1.2',
    'description': """
Include analytic account in stock accounting entries
======================================================
This module adds analytic account field for scrap and
production virtual stock locations.

When stock input account is debited corresponding
analytic entry will be created and linked to journal move.

This is useful for expences accumulation on analytic
account when product is moved to manufacturing virtual location.
""",
    'auto_install': False,
    'demo': [],
    'data': ['views/analytic_stock_view.xml'],
    'installable': True
}
