# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        """ Se sobreescribió desde purchase/models/account_invoice.py:AccountInvoice para que en cada línea se coloque 
            la cuenta contable cuando se requiera
        """
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            if line.account_analytic_id and line.account_analytic_id.account_id and line.product_id.type != 'product':
                data['account_id'] = line.account_analytic_id.account_id.id
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.purchase_id = False
        return {}

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    @api.onchange('account_analytic_id')
    def onchange_analytic_id(self):
        if self.product_id.type != 'product' and self.account_analytic_id and self.account_analytic_id.account_id:
            self.account_id = self.account_analytic_id.account_id
