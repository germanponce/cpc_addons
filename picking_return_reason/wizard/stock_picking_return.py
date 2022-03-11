# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    
    return_reason = fields.Selection(
        [
            ('cred_doc','With Credit Document'),
            ('no_cred_doc','Without Credit Document'),
            ('reship','Reshipment')
        ],
        string='Return reason',
        help="Explanation about this picking at create time from return"
    )
    need_reason = fields.Boolean('Selected picking request a reason to proceed')
    
    @api.model
    def default_get(self, fields):
        res=super(ReturnPicking, self).default_get(fields)
        sp=self.env['stock.picking'].browse(self.env.context.get('active_id'))
        res['need_reason']=sp.picking_type_id.code == 'outgoing'
        return res
    
    @api.multi
    def _create_returns(self):
        sp_id, spt_id = super(ReturnPicking, self)._create_returns()
        if self.need_reason:
            sp=self.env['stock.picking'].browse(sp_id)
            sp.return_reason=self.return_reason
        return sp_id, spt_id
