# -*- coding: utf-8 -*-
from openerp import models, api, fields
import logging
_logger = logging.getLogger(__name__)

class MassReasignacionIniciativas(models.TransientModel):
    _inherit = 'mass.reasignacion.iniciativas'
    
    @api.multi
    def confirm(self):
        _logger.debug('\n\n(0)En MRI.confirm(), context: '+str(self._context))
        if self._context.get('active_model',False)=='llamadas.isep.report':
            dict_ctx=self._context.copy()
            dict_ctx['active_model']='crm.lead'
            aids=self.env['llamadas.isep'].browse(self._context.get('active_ids',False)).mapped('opportunity_id.id')
            dict_ctx['active_ids']=aids
            self=self.with_context(dict_ctx)
        _logger.debug('\n\n(1)En MRI.confirm(), context: '+str(self._context))
        return super(MassReasignacionIniciativas, self).confirm()
            