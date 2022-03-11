# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    
    reference2 = fields.Char('Reference 2')
    office = fields.Char('Office')
    notes = fields.Text('Notes')