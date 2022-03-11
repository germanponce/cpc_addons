# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Exportacion Automatica de Polizas',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
AUTOMATIZACION EXPORTACION DE POLIZAS
=====================================

Configuracion:
    Debemos ingresar la Ruta de Exportacion en la Accion Planificada llamada Programacion de Exportacion de Polizas.
    
    Diarios:
        * Los Diarios que deben Generar un CSV por Poliza debemos marcar en el Diario el campo CSV Individual

    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","purchase_requisition","mail","stock_move_entries"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "account_view.xml",
                    # "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
