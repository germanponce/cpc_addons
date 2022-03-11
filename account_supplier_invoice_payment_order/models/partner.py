# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    payment_journal = fields.Many2one('account.journal', 'Payments account') 
    journal_ids = fields.One2many('journal.payment', 'partner_id', 'Payments Journal')
    
    def _get_journal_per_currency(self, currency_id):
        if currency_id:
            str_ccy="and currency_id=%s" % currency_id
        else:
            str_ccy = ""
        sql="select journal_id from %s where partner_id=%s %s limit 1"
        self.env.cr.execute(sql % (self.env['journal.payment']._table, self.id, str_ccy))
        res=self.env.cr.fetchall()
        return res[0][0] if len(res)>0 else None
