# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.l10n_mx_einvoice import amount_to_text_es_MX
import pytz
import babel
from odoo import tools
import odoo.addons.decimal_precision as dp

class SupplierPaymentOrder(models.TransientModel):
    _name ='account.invoice.payment_order.wizard'

    @api.model  
    def default_get(self, fields):
        res = super(SupplierPaymentOrder, self).default_get(fields)
        record_ids = self._context.get('active_ids', [])
        invoices_to_pay_obj = self.env['account.invoice.supplier_collection_projection']
        if not record_ids:
            return {}

        query = "SELECT partner_id, array_agg(id), currency_id from account_invoice_supplier_collection_projection where id in %s group by partner_id, currency_id"
        
        self._cr.execute(query, (tuple(record_ids),))
        lines = []
        partner_obj = self.env['res.partner']     
        for line in self._cr.fetchall():
            invoices = invoices_to_pay_obj.browse(line[1]).filtered(lambda x: not x.invoice_id.payment_ord_id)
            if len(invoices)<1:
                continue
            amount = sum(invoices.mapped('total'))
            currency = self.env['res.currency'].browse(line[2])
            partner_obj=partner_obj.browse(line[0])
            payment_jrn=self.env['account.journal'].browse(partner_obj._get_journal_per_currency(line[2])).exists()
            
            lines.append((0,0,{
                    'partner_id'    : line[0],
                    'concept'       : 'Pago de Factura(s) ' + (', '.join(x.invoice_id.reference for x in invoices)),
                    'amount_inv'    : amount,
                    'currency_id'   : line[2],
                    'rate'          : (payment_jrn.currency_id.rate or 1)/currency.rate if payment_jrn.id else 0,
                    'amount'        : amount*(payment_jrn.currency_id.rate or 1)/currency.rate if payment_jrn.id else 0,
                    'invoice_ids'   : invoices.mapped('invoice_id.id'),
                    'payment_journal'   : payment_jrn.id,
                    'suppliers_extras'  : partner_obj.suppliers_extras
                    }))
        res.update(lines=lines)
        return res
    
    
    lines = fields.One2many('account.invoice.payment_order.wizard.line','wizard_id',string='Líneas',
                            ondelete="cascade")
    
    
    @api.multi
    def action_get_report(self):
        ai=self.env['account.invoice']
        return self.env['report'].get_action(self.lines.mapped('payment_ord_id'), 'payment_order.account_payment_order_rpt')
    
class SupplierPaymentOrderLine(models.TransientModel):
    _name ='account.invoice.payment_order.wizard.line'

    suppliers_extras = fields.Boolean('Proveedores Varios') 
    supplier_name = fields.Char('Proveedor', size=256)
    supplier_account = fields.Char('Cuenta', size=256)
    supplier_bank = fields.Char('Banco a Pagar', size=256)
    supplier_sucursal = fields.Char('Sucursal', size=256)
    supplier_bank_id = fields.Many2one('res.partner.bank', string="Partner bank account", domain="[('partner_id','=',partner_id)]")
    wizard_id = fields.Many2one('account.invoice.payment_order.wizard', required=True)
    partner_id = fields.Many2one('res.partner', string="Proveedor", readonly=True)
    concept = fields.Char(string="Concepto de Pago", readonly=True)
    amount_inv = fields.Float(string='Importe', readonly=True, digits=dp.get_precision('Account'))
    amount = fields.Float(string='Total', digits=dp.get_precision('Account'))
    currency_id = fields.Many2one('res.currency', string="Moneda", readonly=True)
    notes = fields.Text(string="Observaciones")
    invoice_ids = fields.Many2many('account.invoice')
    payment_ord_id = fields.Integer()
    payment_journal = fields.Many2one('account.journal', string="Payments journal", required=True)
    rate = fields.Float(string='Current Rate', digits=(12, 6), help='The rate of the currency to the currency of rate 1.')
    
    @api.onchange('rate')
    def onchange_rate(self):
        if self.rate:
            self.amount = self.amount_inv*self.rate
            
    @api.onchange('payment_journal')
    def onchange_pay_jrn(self):
        if self.payment_journal:
            self.rate = (self.payment_journal.currency_id.rate or 1)/self.currency_id.rate
    
    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, vals):
        # VSGTN: Comprobaciones en las líneas, si el partner tiene cuentas bancarias y si se definió desde que cuenta se le pagará (partner_id.payment_journal)
        inv_ids = vals.pop('invoice_ids')
        res = super(SupplierPaymentOrderLine, self).create(vals)
        rp_obj=self.env['res.partner'].browse(vals.get('partner_id',None))
        rp_bnk_obj=self.env['res.partner.bank'].browse(vals.get('supplier_bank_id',None))
        partner_cst=vals.get('suppliers_extras',None)
        vals_pord = {
            'partner_extras': partner_cst,
            'partner_name': vals.get('supplier_name',None) if partner_cst else rp_obj.name,
            'partner_account': vals.get('supplier_account',None) if partner_cst else rp_bnk_obj.acc_number,
            'partner_bank': vals.get('supplier_bank',None) if partner_cst else rp_bnk_obj.bank_name,
            'partner_bank_office': vals.get('supplier_sucursal',None) if partner_cst else rp_bnk_obj.office,
            'partner_bank_id': vals.get('supplier_bank_id',None), 
            'partner_id': rp_obj.id,
            'payment_journal': vals.get('payment_journal',None),
            'subject': vals.get('concept',None),
            'date': fields.Date.context_today(self),
            'name': 'OP%s'%self.env.ref('account_supplier_invoice_payment_order.supplier_payment_seq_no').next_by_id(),
            'amount': vals.get('amount',None),
            'rate': vals.get('rate',None),
            'amount_inv': vals.get('amount_inv',None),
            'currency_inv_id': vals.get('currency_id',None),
            'notes': vals.get('notes',None),
        }
        pord = self.env['account.payment.order'].create(vals_pord)
        ai=self.env['account.invoice'].browse(inv_ids)
        ai.write({'payment_ord_id': pord.id})
        res.write({'payment_ord_id': pord.id})
        pord.create_acct_movs(
            self.env['ir.values'].get_default('account.config.settings', 'po_supplier_accnt'),
            self.env['ir.values'].get_default('account.config.settings', 'po_offsetting_accnt'),
            'activate'
        )
        return res
