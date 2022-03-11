# -*- coding: utf-8 -*-

from openerp.osv import fields,osv
from openerp import tools,api

class purchase_report(osv.osv):
    _name = "llamadas.isep.report"
    _description = "Reporte sobre Llamadas ISEP"
    _auto = False
    _columns = {
        'name': fields.char('Nombre', readonly=True),
        'extension': fields.char('Extension', readonly=True),
        'telefono': fields.char('Telefono', readonly=True),
        'date_ini': fields.datetime('Inicio', readonly=True),
        'date_out': fields.datetime('Fin', readonly=True),
        'date_opo': fields.datetime('Fecha de Inicitativa', readonly=True),
        'note': fields.text('Notas', readonly=True),
        'duracion': fields.float('Duración', readonly=True),
        'employee': fields.many2one('hr.employee', "Empleado", readonly=True),
        'opportunity_id': fields.many2one('crm.lead', string="Iniciativa", readonly=True),
        'entidad': fields.char("Entidad", readonly=True),
        'empleado': fields.many2one('hr.employee', "Empleado", readonly=True),
        'user_id': fields.many2one('res.users', "Usuario Iniciativa", readonly=True),
        'notas': fields.text("Detalles llamada", readonly=True),
        'efectiva': fields.boolean("Contacto efectivo", readonly=True),
        'check_employee': fields.boolean("Empleado", readonly=True),
        'llamadas_id': fields.many2one("res.partner","Cliente", readonly=True),
        'cuenta': fields.integer('# of Lines', readonly=True),
    }
    _order = 'date_out desc, cuenta desc'
    
    @api.multi
    def regopen(self):
        res = self.get_formview_action()[0]
        res.pop('context')
        res.pop('views')
        res['view_type'] = 'form'
        res['view_id'] = [self.env.ref('isep_custom.view_call_form').id]
        
        return res
    
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'llamadas_isep_report')
        cr.execute("""
            create or replace view llamadas_isep_report as (
                select
                    li.id,
                    li.name,
                    li.extension,
                    li.telefono,
                    li.date_ini,
                    li.date_out,
                    cl.create_date as date_opo,
                    li.note,
                    li.duracion,
                    li.employee,
                    li.opportunity_id,
                    li.entidad,
                    li.empleado,
                    cl.user_id,
                    li.notas,
                    li.efectiva,
                    li.check_employee,
                    li.llamadas_id,
                    sq.cuenta
                from llamadas_isep li
                    inner join
                        (select llamadas_id, count(id) as cuenta from llamadas_isep group by llamadas_id) as sq
                    on li.llamadas_id=sq.llamadas_id
                    inner join
                        crm_lead as cl 
                    on li.opportunity_id=cl.id
            )
        """)
    