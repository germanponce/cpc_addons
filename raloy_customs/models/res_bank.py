# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    
    @api.multi
    def name_get(self):
        return [
            (c.id, 
            tools.ustr(
                (c.acc_number and '[' + c.acc_number + '] - ' or '') + 
                (c.bank_id.name or '') + 
                ', ' + 
                (c.currency_id.name or '')
            )
        ) for c in self]
