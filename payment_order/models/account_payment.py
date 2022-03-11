# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class account_payment(models.Model):
    _inherit = "account.payment"
    
    payment_ord_id = fields.Many2one('account.payment.order', string="Payment Order")
    
    @api.multi
    def print_po_srv(self):
        rec_ids = self.env.context.get('active_ids', False)
        if not rec_ids:
            raise UserError(_('Warning !\nNo records selected.'))
        recs = self.browse(rec_ids)
        for rec in recs:
            if rec.mapped('invoice_ids'):
                raise UserError(_("Warning!\nAt least a record is related to invoices."))
            if rec.state!='posted':
                raise UserError(_("Warning!\nAt least a record is not on Posted state."))
            if recs.payment_type!='outbound':
                raise UserError(_("Warning!\nAt least a record is not Outbound type."))
        po_obj = self.env['account.payment.order']
        for rec in recs:
            rate = (rec.journal_id.currency_id.rate or 1)/rec.currency_id.rate
            vals = {
                'partner_extras': rec.suppliers_extras,
                'partner_name': rec.supplier_name if rec.suppliers_extras else rec.partner_id.name,
                'partner_account': rec.supplier_account if rec.suppliers_extras else rec.partner_acc_id.acc_number,
                'partner_bank': rec.supplier_bank if rec.suppliers_extras else rec.partner_acc_id.bank_id.name,
                'partner_bank_office': rec.supplier_sucursal if rec.suppliers_extras else rec.partner_acc_id.office,
                'partner_bank_id': rec.partner_acc_id.id,
                'partner_id': rec.partner_id.id,
                'payment_journal': rec.journal_id.id,
                'subject': rec.communication,
                'date': fields.Date.context_today(self),
                'name': 'OP%s'%self.env.ref('account_supplier_invoice_payment_order.supplier_payment_seq_no').next_by_id(),
                'amount': rec.amount*rate,
                'rate': rate,
                'amount_inv': rec.amount,
                'currency_inv_id': rec.currency_id.id,
                'notes': '',
                'state': 'done',
            }
            id_po=po_obj.create(vals)
            rec.payment_ord_id = id_po.id
        return self.env['report'].get_action(rec.mapped('payment_ord_id'), 'payment_order.account_payment_order_rpt')

    @api.multi
    def cancel(self):
        res = super(account_payment, self).cancel()
        for rec in self.filtered(lambda l: l.payment_ord_id):
            rec.payment_ord_id.write({'state' : 'cancel'})
    
class account_register_payments(models.TransientModel):
    _name = "account.register.payments.po"
    _inherit = 'account.abstract.payment'
    _description = "Register payments on Payment Orders"
    
    def _get_invoices(self):
        return self.env['account.invoice'].browse(self.env.context.get('invoice_ids'))
    
    check_amount_in_words = fields.Char(string="Amount in Words")
    check_manual_sequencing = fields.Boolean(related='journal_id.check_manual_sequencing')
    check_number = fields.Integer(string="Check Number", readonly=True, copy=False, default=0,
        help="Number of the check corresponding to this payment. If your pre-printed check are not already numbered, "
             "you can manage the numbering in the journal configuration page.")
    cmpl_type = fields.Selection([('check', 'Cheque'), 
        ('transfer', 'Transferencia'), 
        ('payment', 'Otro método de pago')], 
        string='Tipo de complemento', 
        help='Indique el tipo de complemento a usar para este pago.'
    )
    partner_acc_id  = fields.Many2one('res.partner.bank', string='Cuenta Bancaria')
    partner_parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='Parent Partner')
    other_payment   = fields.Many2one('eaccount.payment.methods', string='Método de Pago SAT')

    @api.onchange('journal_id')
    def _onchange_journal(self):
        return {}
    
    @api.model
    def default_get(self, fields):
        rec = super(account_register_payments, self).default_get(fields)

        rec.update({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
        })
        return rec

    def get_payment_vals(self):
        """ Hook for extension """
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
            'payment_type': self.payment_type,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
            'cmpl_type': self.cmpl_type,
            'partner_acc_id': self.partner_acc_id.id,
            'other_payment': self.other_payment.id,
        }

    @api.multi
    def create_payment(self):
        payment = self.env['account.payment'].create(self.get_payment_vals())
        payment.post()
        po=self.env['account.payment.order'].browse(self.env.context.get('payment_order_id'))
        po.state='done'
        po.create_acct_movs(
            self.env['ir.values'].get_default('account.config.settings', 'po_offsetting_accnt'),
            self.env['ir.values'].get_default('account.config.settings', 'po_supplier_accnt'),
            'payment'
        )
        
        return {'type': 'ir.actions.act_window_close'}
