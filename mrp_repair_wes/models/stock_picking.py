# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"
    
    @api.multi
    @api.depends('picking_type_id')
    def _get_repair_type(self):
        for item in self:
            item.repair_type = (self.env.ref('mrp_repair_wes.stock_picking_type_repair').id == item.picking_type_id.id)
    
    repair_type = fields.Boolean(compute='_get_repair_type')
    repair_ids = fields.One2many('mrp.repair', 'picking_id', 'Repair Orders')
    
    @api.onchange('picking_type_id')
    def onchange_picking_type_wes(self):
        if self.repair_type:
            return {
                'domain': {
                    'partner_id': [('repair_partner','=',True)]
                }
            }
        else:
            return {
                'domain': {
                    'partner_id': []
                }
            }
    
    @api.multi
    def do_new_transfer(self):
        res = super(Picking, self).do_new_transfer()
        #VSGTN: Corroborar backorder
        if res == None and self.repair_type:
            res = {
                    'type': 'ir.actions.act_window',
                    'res_model': 'mrp.repair',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context': "{'from_picking': %s}" % (self.id),
                    'target': 'new',
                }
        return res
