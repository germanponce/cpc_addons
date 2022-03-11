# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Extension de Solicitudes',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
Origenes de Compra en Solicitudes
=================================

Este modulo añade una relacion directa de los Pedidos de compra creados desde una Solicitud.


    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","purchase_requisition","mail","fincamiento"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    # "purchase_view.xml",
                    # "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
