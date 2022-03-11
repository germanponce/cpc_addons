# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class PurchaseConfig(models.TransientModel):
    _inherit = 'purchase.config.settings'
    
    stock_location = fields.Many2one('stock.location', string='Location for stock availability', 
                                     help='Select the location where stock must be available for comparison')
    stock_product = fields.Many2one('stock.location', string='Location for product stock availability', 
                                     help='Select the location where product stock must be available for comparison')
    
    @api.multi
    def set_stock_location_defaults(self):
        res = self.env['ir.values'].sudo().set_default('purchase.config.settings', 'stock_location', self.stock_location.id)
        return res
        
    @api.multi
    def set_stock_product_defaults(self):
        res = self.env['ir.values'].sudo().set_default('purchase.config.settings', 'stock_product', self.stock_product.id)
        return res
