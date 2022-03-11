# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class res_store(models.Model):
    _inherit = "res.store"
    
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')
