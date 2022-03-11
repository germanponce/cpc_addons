# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """ Es necesario sobreescribir el método de purchase/models/account_invoice.py:AccountInvoice, 
            pero la llamada a la clase base (account/models/account_invoice.py:AccountInvoice debe preservarse
            ya que ajusta algunos datos importantes.
        """
        from odoo.addons.purchase.models import account_invoice
        res=super(account_invoice.AccountInvoice, self)._onchange_partner_id()
        #Si se llamaba a la clase padre inmediata, se ajustaba también el contexto, por lo que la asignación no funcionaba
        if self.purchase_id and self.purchase_id.store_id:
            self.journal_id=self.purchase_id.store_id.journal_ids[0].id
        #Se reestablece la posición fiscal en la llamada a la función padre, por lo que se leerá directamente de la sucursal
        if self.store_id:
            self.fiscal_position_id=self.store_id.fiscal_position_id.id
        return res
    
    @api.onchange('partner_shipping_id')
    def _onchange_partner_shipping_id(self):
        """ Es necesario sobreescribir el método de sale/models/account_invoice.py:AccountInvoice ya que tal característica 
            nunca se usará por el cómo se implementó el proyecto
        """
        return
    
    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        if self.purchase_id:
            self.journal_id=self.purchase_id.store_id.journal_ids[0].id
            self.fiscal_position_id=self.purchase_id.store_id.fiscal_position_id.id
            
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    def _compute_il_tax_ids(self):
        for record in self:
            record.invoice_line_tax_ids_ro=record.invoice_line_tax_ids
    
    invoice_line_tax_ids_ro = fields.Many2many('account.tax', compute='_compute_il_tax_ids', string='Taxes')
