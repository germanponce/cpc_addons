# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Importacion Automatica de Polizas',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
IMPORTACION Y CONCILIACION DE POLIZAS
=====================================

Configuracion:
    Debemos ingresar la Ruta de Importacion en la Accion Planificada llamada Importacion de Polizas de Proveedores.
    * Obversaremos 2 Rutas:
        * Una nos indica donde tomaremos los archivos y la segunda una vez procesados a que lugar los moveremos.

    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","purchase_requisition","mail","cron_export_moves"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "account_view.xml",
                    # "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
