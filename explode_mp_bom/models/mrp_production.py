# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    @api.multi
    def project_bom(self):
        context = self._context
        if context.get('origin_action',False) and context['origin_action'] == self.env.ref('mrp.mrp_production_action_planning').id:
            #Falta filtrar que los productos no sean EPTs
            if not context.get('active_ids', False):
                raise UserError(_('Warning !\nNo records selected.'))
            mps = self.env['mrp.production'].search([
                ('id','in',context['active_ids']),
                ('product_id.sale_ok','=',True),
                ('product_id.purchase_ok','=',False),
                ('product_id.can_be_expensed','=',False)
            ])
            values_sql=','.join(mps.mapped(lambda x: '(%d)'%x.id))
            sql = """
                delete from explode_mp_bom_config;
                insert into explode_mp_bom_config values %s;
            """ % (values_sql)
            self.env.cr.execute(sql)
            values_names=', '.join(mps.mapped(lambda x: '%s'%x.name))
            return {
                'type': 'ir.actions.act_window',
                'name': _('Material needs for %s')%values_names,
                'res_model': 'explode.mp.bom',
                'view_mode': 'tree',
                'view_type': 'form',
                'views': [(False, 'tree')],
                'target': 'main',
                #'context': {'search_default_groupby_categ_id': True},
            }
        raise UserError(_('Warning !\nOnly will work on Planning Production Order.'))
    