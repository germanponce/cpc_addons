# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    bank_acc_number = fields.Char(related='payment_journal.bank_acc_number', readonly=True)
    partner_bank_ids = fields.One2many('res.partner.bank', 'partner_id', 'Partner Bank Accounts')
