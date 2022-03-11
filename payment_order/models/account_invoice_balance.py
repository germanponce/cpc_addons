# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SupplierPaymentOrderLine(models.TransientModel):
    _inherit='account.invoice.payment_order.wizard.line'
    
    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, vals):
        # Comprobaciones en las líneas, si el partner tiene cuentas bancarias y si se definió desde que cuenta se le pagará (partner_id.payment_journal)
        res = super(SupplierPaymentOrderLine, self).create(vals)
        vals_pord = {
            'partner_extras': vals.get('supplier_extras',None),
            'partner_name': vals.get('supplier_name',None),
            'partner_account': vals.get('supplier_account',None),
            'partner_bank': vals.get('supplier_bank',None),
            'partner_bank_office': vals.get('supplier_sucursal',None),
            'partner_id': vals.get('partner_id',None),
            'subject': vals.get('concept',None),
            'date': fields.Date.context_today(self),
            'name': self.env.ref('account_supplier_invoice_payment_order.supplier_payment_seq_no').next_by_id(),
            'amount': vals.get('amount',None),
            'currency_id': vals.get('currency_id',None),
            'notes': vals.get('notes',None),
            'invoice_ids': vals.get('invoice_ids',None),
        }
        pord = self.env['account.payment.order'].create()
        return res
