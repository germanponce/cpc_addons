# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class PurchaseCateg(models.Model):
    _name = 'purchase.category'
    _order = 'name'
    
    name = fields.Char('Name', index=True, required=True)
    
