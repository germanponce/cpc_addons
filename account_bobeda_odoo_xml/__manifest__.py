# -*- encoding: utf-8 -*-

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

{
    'name' : 'Inetgración Bobeda Fiscal',
    'description' : """


Integración y Validaciones con Bobeda Fiscal

        - Campo UUID Unico y Obligatorio
        - Instalacion de la Libreria:
            - pip install mysql-connector-python-rf
            - https://pypi.python.org/pypi/mysql-connector-python-rf
        - Existe un Parametro dentro de Odoo, el cual nos permite tener un margen de tolerancia para validar las Facturas.
            - bobeda_tolerance_range_between_invoice_record_and_cfdi_xml_file
        - Instalar el mysqldb de python
            - udo apt-get install python-mysqldb
        - Debemos configurar los accesos a la Base de Datos para la Bobeda Fiscal
            - Ingresamos al menu Contabilidad --> Compras --> Configuración Bobeda Fiscal
            - Ingresamos
                - Usuario
                - Contraseña
                - Host
                - Base de Datos
            - Solo se mostrara la informacion anterior habilitando el modo de Desarrollador.
        - Consulta de Bobeda Fiscal
            - Debemos Seleccionar el Boton Consultar Bobeda Fiscal, el cual insertara el UUID Seleccionado en el Asistente.
            
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
                'security/ir.model.access.csv'
                ],
    'demo_xml' : [],
    'installable' : True,
    'auto_install' : False
}
# Revision: 2.9
# Release: 1.2
