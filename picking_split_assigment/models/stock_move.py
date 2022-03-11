# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"
    
    @api.multi
    def assign_picking(self):
        Picking = self.env['stock.picking']
        for move in self:
            picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            move.recompute()
        return True
    _picking_assign = assign_picking
