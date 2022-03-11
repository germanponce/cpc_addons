# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class account_payment(models.Model):
    _inherit = 'account.payment'
    
    @api.onchange('partner_id')
    def _onchange_select_partner_journal_id(self):
        if self.env.context.get('default_journal_id'):
            return
        if self.partner_id:
            if self.invoice_ids:
                ccys = self.invoice_ids.mapped('currency_id')
                if len(ccys)!=1:
                    return
            else:
                ccys = self.partner_id.property_purchase_currency_id
            self.journal_id=self.partner_id._get_journal_per_currency(ccys.id)

class account_payment(models.TransientModel):
    _inherit = 'account.register.payments'

    @api.onchange('partner_id')
    def _onchange_select_partner_journal_id(self):
        if self.partner_id:
            self.journal_id=self.partner_id._get_journal_per_currency(self.currency_id.id)
