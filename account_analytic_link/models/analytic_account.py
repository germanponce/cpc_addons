# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    account_id = fields.Many2one('account.account', string="Account")
