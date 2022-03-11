# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.l10n_mx_einvoice import amount_to_text_es_MX
from odoo.tools import datetime
import odoo.addons.decimal_precision as dp
import babel

class PaymentOrder(models.Model):
    _name = 'account.payment.order'
    _order = 'id desc'

    state = fields.Selection([('active','Active'), ('cancel','Cancelled'), ('done', 'Done')], readonly=True, string='State', default='active')
    partner_extras = fields.Boolean('Custom partner') 
    partner_name = fields.Char('Supplier', size=256)
    partner_account = fields.Char('Account', size=256)
    partner_bank = fields.Char('Bank', size=256)
    partner_bank_office = fields.Char('Bank Office', size=256)
    partner_id = fields.Many2one('res.partner', string="Supplier ID")
    partner_bank_id = fields.Many2one('res.partner.bank', string="Partner bank account")
    payment_journal = fields.Many2one('account.journal', string="Payments journal")
    subject = fields.Char(string="Payment subject")
    date = fields.Date(string='Payment Order Date', default=fields.Date.context_today, required=True, copy=False)
    name = fields.Char(readonly=True, copy=False, default="Draft Payment Order")
    amount_inv = fields.Float(string='Amount Inv', digits=dp.get_precision('Account'))
    amount = fields.Float(string='Amount', digits=dp.get_precision('Account'))
    currency_inv_id = fields.Many2one('res.currency', string="Original Currency")
    notes = fields.Text(string="Annotations")
    invoice_ids = fields.One2many('account.invoice', 'payment_ord_id', 'Invoices')
    payment_ids = fields.One2many('account.payment', 'payment_ord_id', 'Payments')
    invoice_hist_ids = fields.Many2many('account.invoice', string="Invoices (Hist)")
    payment_hist_ids = fields.Many2many('account.payment', string="Payments (Hist)")
    rate = fields.Float(string='Current Rate', digits=(12, 6), help='The rate of the currency to the currency of rate 1.')
    act_acct_move = fields.Many2one('account.move', string="Account Move on creation")
    pay_acct_move = fields.Many2one('account.move', string="Account Move on payment")
    
    def create_acct_movs(self, id_cta_abono, id_cta_cargo, mov_type):
        ln_abono_vls = {
            'account_id': id_cta_abono,
            'name': self.name,
            'partner_id': self.partner_id.id,
            'credit': self.amount,
            'debit': 0,
        }
        ln_cargo_vls = {
            'account_id': id_cta_cargo,
            'name': self.name,
            'partner_id': self.partner_id.id,
            'credit': 0,
            'debit': self.amount,
        }
        if self.rate != 1:
            ln_cur = {
                'amount_currency': self.amount_inv,
                'currency_id': self.currency_inv_id.id,
            }
            ln_cargo_vls.update(ln_cur)
            ln_cur['amount_currency'] = ln_cur['amount_currency']/-1
            ln_abono_vls.update(ln_cur)
        
        mv_vals={
            'journal_id': self.env['ir.values'].get_default('account.config.settings', 'po_journal'),
            'ref': self.name,
            'date': fields.Datetime.now(),
            'line_ids': [
                (0, 0, ln_abono_vls),
                (0, 0, ln_cargo_vls)
            ]
        }
        res=self.env['account.move'].create(mv_vals)
        res.post()
        
        if mov_type == 'activate':
            self.act_acct_move = res.id
        else:
            self.pay_acct_move = res.id
    
    def _get_amount_to_text(self, amount_total, currency_name):
        return amount_to_text_es_MX.get_amount_to_text(self, amount_total, currency_name)
    
    def _date_fmt(self):
        return babel.dates.format_date(date=datetime.strptime(self.date,'%Y-%m-%d'), format='EEEE d MMMM y', locale=self.env.user.lang)

    @api.multi
    def button_payment_register(self):
        action=self.env.ref('account.action_account_payment_from_invoices')
        return {
            'name': _(action.name),
            'res_model': 'account.register.payments.po',
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'context': {
                'invoice_ids': self.invoice_ids.mapped('id'),
                'default_journal_id': self.payment_journal.id,
                'default_hide_payment_method': False,
                # ¿Qué sucederá cuando son proveedores varios?
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount,
                'default_communication': "(%s) %s" % (self.name, self.subject),
                'default_currency_id': self.payment_journal.currency_id.id,
                'payment_order_id': self.id,
            },
            'target': action.target,
            'type': action.type,
        }
    
    def btn_cancel(self):
        if self.invoice_ids:
            self.invoice_hist_ids = [(6,0,self.invoice_ids.mapped('id'))]
            self.invoice_ids = [(5,0,0)]
            
        if self.payment_ids:
            self.payment_hist_ids = [(6,0,self.payment_ids.mapped('id'))]
            self.payment_ids = [(5,0,0)]
            
        self.state='cancel'

        ia=self.env['ir.attachment'].search([('res_model','=',self._name),('res_id','=',self.id)])
        if ia:
            ia.unlink()
        
        self.act_acct_move.button_cancel()
