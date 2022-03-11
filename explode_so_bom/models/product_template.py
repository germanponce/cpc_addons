# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    stock_offset = fields.Integer('Stock Offset', default=0, help='Stock offset for leveling', track_visibility='onchange')
    
    _sql_constraints= [
        ('stock_offset_pos', 'check (stock_offset >= 0)', "Only 0 and positive values!"),
    ]
