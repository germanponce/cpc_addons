# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    @api.one
    def _set_check_next_number(self):
        if self.check_sequence_id:
            self.check_sequence_id.sudo().number_next_actual = self.check_next_number
