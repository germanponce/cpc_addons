# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.l10n_mx_einvoice import amount_to_text_es_MX
import pytz
import babel
from odoo import tools

class account_invoice_supplier_collection_projection(models.Model):
    _inherit = 'account.invoice.supplier_balance_due'
    
    def _now(self):
        utz=pytz.timezone(self.env.user.tz)
        now = tools.datetime.now(utz)
        return babel.dates.format_date(date=now, format='EEEE d MMMM y', locale=self.env.user.lang)
    
    def get_amount_to_text(self, amount_total, currency_name):
        return amount_to_text_es_MX.get_amount_to_text(self, amount_total, currency_name)
    
    @api.multi
    def _get_invoices_per_partner(self, ids):
        query = "SELECT partner_id, array_agg(id) from account_invoice_supplier_collection_projection where id in %s group by partner_id"
        
        self._cr.execute(query, (tuple(ids),))
        return self.env.cr.fetchall()
