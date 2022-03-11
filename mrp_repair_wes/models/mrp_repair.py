# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from openerp.exceptions import UserError

class Repair(models.Model):
    _inherit = 'mrp.repair'
    
    @api.model
    def _default_stock_location(self):
        return self.env.ref('mrp_repair_wes.stock_location_repair', raise_if_not_found=False)
    
    location_id = fields.Many2one(default=_default_stock_location)
    
    partslist_id = fields.Many2one('mrp.repair.wes.partslist', 'Parts List', readonly=True, states={'draft': [('readonly', False)]})
    route_id = fields.Many2one('mrp.repair.wes.route', 'Route', readonly=True, states={'draft': [('readonly', False)]})
    activities_lines = fields.One2many('mrp.repair.wes.activity.line', 'repair_id', 'Activities for this repairing')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    
    partnum_id = fields.Many2one('mrp.repair.wes.partnum', 'Part number', required=True)
    parttype_id = fields.Many2one(related='partnum_id.type_id')
    partsubt_id = fields.Many2one(related='partnum_id.subtype_id')
    repcause_id = fields.Many2one('mrp.repair.wes.cause', 'Repair Cause', required=True)
    reptype_id = fields.Many2one('mrp.repair.wes.type', 'Repair Type', required=True)
    observations = fields.Text('Observations')
    
    description = fields.Char('Description')
    on_document = fields.Char('On document')
    rosh = fields.Boolean('ROHS')
    serialized = fields.Boolean('Serialized')
    serial = fields.Char('No. Number')
    mroc = fields.Char('MROc')
    assigned_user = fields.Many2one('res.partner', 'Assigned User')
    track_label = fields.Char('Tracking Label')
    fault_tag = fields.Char('Fault Tag No.')
    assembly_no = fields.Char('Assembly No.')
    site_code = fields.Char('Site Data Code')
    log_no = fields.Char('LogNo')
    eng_badge_no = fields.Char('Eng Badge No.')
    swap_date = date = fields.Date('Swap Date', index=True, default=fields.Date.context_today)
    fab_rev = fields.Char('Fab Rev')
    rev_in = fields.Char('Rev IN')
    rev_out = fields.Char('Rev OUT')
    provider = fields.Char('Provider')
    hdd_serial = fields.Char('HDD Serial')
    hp_pn = fields.Char('HP PN')
    ct_num = fields.Char('CT Number')
    hp_sec_label = fields.Char('HP Security Label')
    firmware_in = fields.Char('Firmware IN')
    hp_model = fields.Char('HP Model')
    capacity = fields.Char('Capacity')
    restrictions = fields.Char('Restrictions')
    
    is_hdd = fields.Boolean(related='product_id.is_hdd')
    next_item = fields.Boolean()
    
    @api.onchange('partslist_id')
    def onchange_partslist_id(self):
        if len(self.operations) == 0:
            for op in self.partslist_id.operations:
                self.operations += self.operations.new({'type': op.type, 'product_id': op.product_id, 'name': op.name, 'location_id': op.location_id, 
                                             'location_dest_id': op.location_dest_id, 'product_uom_qty': op.product_uom_qty*self.product_qty, 'product_uom': op.product_id.uom_id,
                                             'price_unit': op.price_unit, 'tax_id': op.tax_id, 'to_invoice': op.to_invoice})
    
    @api.onchange('route_id')
    def onchange_route_id(self):
        if len(self.activities_lines) == 0:
            for act in self.route_id.activities_ids:
                self.activities_lines += self.activities_lines.new({'activity_id': act.id, 'required_hours': act.planned_hours*self.product_qty})
    
    @api.multi
    def done_edit(self):
        res = {}
        if self.next_item:
            res = {
                        'type': 'ir.actions.act_window',
                        'res_model': 'mrp.repair',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'context': "{'from_picking': %s}" % (self.picking_id.id),
                        'target': 'new',
                    }
        self.write({'picking_id': self.picking_id.id, 'next_item': False})
        return res
    
    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(Repair, self).default_get(default_fields)
        
        if 'from_picking' in context:
            picking_id = context['from_picking']
            picking = self.env['stock.picking'].browse(picking_id)
            pendings = set(picking.mapped('pack_operation_product_ids.product_id.id')) - set(picking.mapped('repair_ids.product_id.id'))
            
            if len(pendings) > 0:
                next_item = False
                pending_op = pendings.pop()
                if len(pendings) > 0:
                    next_item = True
                product_op = picking.pack_operation_product_ids.filtered(lambda r: r.product_id.id == pending_op)
                res['product_id'] = product_op.product_id.id
                res['product_qty'] = product_op.product_qty
                res['product_uom'] = product_op.product_uom_id.id
                res['picking_id'] = picking_id
                res['next_item'] = next_item
            else:
                raise UserError(_('Warning !\nNo more products to repair.')) 
        return res
    