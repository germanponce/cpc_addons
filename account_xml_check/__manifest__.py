# -*- encoding: utf-8 -*-

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

{
    'name' : 'Contabilidad electrónica para México',
    'description' : """
    Adecuación para cumplir con los requisitos de la Facturacion Electronica de Proveedores:

        - Validacion de RFC del XML Adjunto
        - Validacion de Montos


         """,
    'version' : '1.0',
    'author' : 'ASTI & Argil',
    'website' : 'http://www.argil.mx',
    'license' : 'GPL-3',
    'category' : 'Accounting',
    'depends' : ['base', 
                 'account',
                ],
    'data' : [
                'invoice_fit_view.xml',
                ],
    'demo_xml' : [],
    'installable' : True,
    'auto_install' : False
}
# Revision: 2.9
# Release: 1.2
