# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    payment_ord_id = fields.Many2one('account.payment.order', string="Payment Order")
    payment_ord_bank = fields.Char('Payment order bank', related='payment_ord_id.partner_bank')
    payment_journal = fields.Many2one('account.journal', 'Payment journal', related='payment_ord_id.payment_journal')
