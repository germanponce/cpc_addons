# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class JournalPayment(models.Model):
    _name = 'journal.payment'
    
    partner_id = fields.Many2one('res.partner', 'Partner')
    journal_id = fields.Many2one('account.journal', 'Payments account') 
    currency_id = fields.Many2one('res.currency', 'Currency')
    bank_acc_number = fields.Char(related='journal_id.bank_acc_number', readonly=True)
