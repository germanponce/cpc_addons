# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleConfiguration(models.TransientModel):
    _inherit = 'account.config.settings'
    
    days_limit_projection = fields.Selection([(7, 'Semanal'), (30, 'Mensual')], default=7, string='Rango Proyeccion Columnas', 
                                           help='Days for every column width.')
    
    @api.multi
    def set_days_limit_projection_defaults(self):
        res = self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'days_limit_projection', self.days_limit_projection)
        self.env['account.invoice.customer_collection_projection'].init()
        return res