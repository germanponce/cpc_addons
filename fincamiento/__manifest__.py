# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)

##############################################################################
{
    'name': 'Proceso de Fincamiento y Autorizacion',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Corona",
    'description': """
    
PROCESO DE FINCAMIENTO
======================

Configuracion:
    - Debemos identificar los Proveedores Fincados para ello activamos el campo llamado Fincamiento Automatico.
    - Automaticamente nos pedira una Referencia de Fincamiento con la cual podemos referenciar los Presupuestos de Fincamiento.

Referencias de Fincamiento:
    - Una vez que Validamos un Presupuesto Fincado con un Proveedor, podemos cancelar los Presupuestos pendientes con la misma Referencia Fincada.
    - Dentro de la Referencia de Fincamiento tenemos un Boton para Cancelar todos los presupuestos fincados no Aprobados.

Funcionalidades:
    - Tenemos un menu especial llamado Evaluacion de Proveedores, al cual podemos acceder desde Compras --> Control --> Evaluacion de Proveedores.
        - Podemos Observar en Color Rojo aquellos Presupuestos Fincados con el mejor Precio.
        - Podemos Observar en Color Verde aquellos Presupuestos Fincados con la mejor fecha de entrega.
    - En Acuerdos de Compra tenemos la posibilidad de Crear Pedidos de Compra para:
        - Proveedores Fincados
        - Articulos sin Proveedor Fincado
        - Ambos

PROCESO DE AUTORIZACION
=======================

Configuracion:
    - Debemos identificar los Proveedores Autorizados para ello activamos el campo llamado Autorizado.



    """,
    "website" : "http://argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","purchase_requisition","mail"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "purchase_view.xml",
                    # "report.xml",
                    ],
    "installable" : True,
    "active" : False,
}
