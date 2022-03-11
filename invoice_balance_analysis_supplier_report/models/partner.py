# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    payment_journal = fields.Many2one('account.journal', 'Payments account') 