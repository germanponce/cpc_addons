# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Reglas de Abastecimiento Extendidas',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
Agrupacion de Acuerdos desde Reglas de Abastecimiento
=====================================================

Configuracion:
    - Productos --> Inventario --> Abastecimiento --> Proponer una Licitación.

Agrupa las licitaciones.

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
