# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        ''' Reescrito desde purchase/models/purchase.py:PurchaseOrder para omitir la posición fiscal
        '''
        if not self.partner_id:
            self.payment_term_id = False
            self.currency_id = False
        else:
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id.id
            self.currency_id = self.partner_id.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id
        return {}
    
    @api.onchange('requisition_id')
    def _onchange_req_id(self):
        if self.requisition_id:
            self.fiscal_position_id=self.requisition_id.picking_type_id.store_id.fiscal_position_id.id
            
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    def _compute_taxes_ro(self):
        for record in self:
            record.taxes_id_ro=record.taxes_id
    
    taxes_id_ro = fields.Many2many('account.tax', compute='_compute_taxes_ro', string='Taxes')
