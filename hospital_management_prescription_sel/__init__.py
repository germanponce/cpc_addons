# -*- coding: utf-8 -*-

import models,wizard

def set_post_init(cr,registry):
    from odoo.api import Environment, SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})
    tmp=env.ref('hospital_management.report_print_prescription')
    #VSGTN: ¿Será necesario corroborar exista el reporte?
    if tmp.ir_values_id:
        tmp.unlink_action()
        
def reset_deps(cr, registry):
    from odoo.api import Environment, SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})
    tmp=env.ref('hospital_management.report_print_prescription')
    tmp.create_action()
