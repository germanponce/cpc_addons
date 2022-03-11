# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Compras Locales',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
Compras Locales ==> 1 Paso
==========================

Configuracion:
    - Las Requisiciones de Compra, asi como la Compra directa pueden omitir las reglas de Recepcion de 2 Pasos a 1 solo, para ello deben Activar el Campo Compra Local (1 Paso).

Lo Anterior directamente creara un solo Albaran.

    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","stock","purchase_requisition","mail","fincamiento"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "stock_view.xml",
                    # "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
