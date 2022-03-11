# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Evaluacion Cotizaciones Compra',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
Evaluacion Cotizaciones Compra
==============================

Podemos Acceder al Menu Evaluacion de Presupuestos desde el Menu Compras --> Control --> Evaluacion de Presupuestos

Este nos indicara por Colores cual tiene mejor fecha de entrega y cual mejor precio.
    * Verde --> Mejor fecha de entrega
    * Rojo --> Mejor Precio

    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","purchase_requisition","mail","fincamiento"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "purchase_view.xml",
                    # "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
