# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Perfiles Compras y Almacenes',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
Restricciones de Compra y Almacen
=================================

Configuracion:
    - Existen 2 Campos en la Ficha de Usuarios
        - Almacenes
        - Categorias de Productos

Estos campos permiten crear las restricciones a los usuarios.


    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","purchase_requisition","mail","fincamiento"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "stock_view.xml",
                    # "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
