# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"
    
    @api.multi
    @api.depends('state')
    def _get_repair_type(self):
        for item in self:
            item.repair_type = self.env.context.get('repair_type')
    
    repair_type = fields.Boolean(compute='_get_repair_type')
    
    @api.onchange('state')
    def onchange_state(self):
        if self.repair_type:
            return {
                'domain': {
                    'product_id': [('categ_id.repairable_prod','=',True)]
                }
            }
        else:
            return {
                'domain': {
                    'product_id': [('type', 'in', ['product', 'consu'])]
                }
            }
