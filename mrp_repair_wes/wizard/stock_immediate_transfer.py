# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    
    @api.multi
    def process(self):
        print "Self: ", self
        
        super(StockImmediateTransfer, self).process()
        
        if self.pick_id.repair_type:
            # VSGTN
            '''
            return {
                    'type': 'ir.actions.client',
                    'tag': 'action_notify',
                    'name': 'Failure',
                    'params': {
                        'title': _('Insight!'),
                        'text': _("(TP) Punto de prueba 5")
                    }
                }
            '''
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'mrp.repair',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context': "{'from_picking': %s}" % (self.pick_id.id),
                    'target': 'new',
                }
