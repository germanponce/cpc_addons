# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class AccountSettings(models.TransientModel):
    _inherit = 'account.config.settings'
    
    po_customer_accnt = fields.Many2one('account.account',string="Account for customer Payment Order")
    po_supplier_accnt = fields.Many2one('account.account',string="Account for supplier Payment Order")
    po_offsetting_accnt = fields.Many2one('account.account',string="Payment Orders offsetting account")
    po_journal = fields.Many2one('account.journal', string="Journal for Payment Orders")
    
    @api.multi
    def set_po_customer_accnt_defaults(self):
        res = self.env['ir.values'].sudo().set_default('account.config.settings', 'po_customer_accnt', self.po_customer_accnt.id)
        return res
        
    @api.multi
    def set_po_supplier_accnt_defaults(self):
        res = self.env['ir.values'].sudo().set_default('account.config.settings', 'po_supplier_accnt', self.po_supplier_accnt.id)
        return res
        
    @api.multi
    def set_po_offsetting_accnt_defaults(self):
        res = self.env['ir.values'].sudo().set_default('account.config.settings', 'po_offsetting_accnt', self.po_offsetting_accnt.id)
        return res
        
    @api.multi
    def set_po_journal_defaults(self):
        res = self.env['ir.values'].sudo().set_default('account.config.settings', 'po_journal', self.po_journal.id)
        return res
