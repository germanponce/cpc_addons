# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    purchase_clasif = fields.Many2one('purchase.category', 'Purchase Category', index=True)
