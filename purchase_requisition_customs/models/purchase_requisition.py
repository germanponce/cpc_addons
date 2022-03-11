# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    
    local_purchase = fields.Boolean(track_visibility='onchange')
    last_parent = fields.Integer(compute='_compute_aaa_sel', readonly=False, 
         default=lambda self: self.env['account.analytic.account'].search([('name','=','000 CPC')]).id)
    account_analytic_id_sel = fields.Many2one('account.analytic.account', string='Analytic Account', compute='_compute_aaa_sel', 
         readonly=False)
    
    @api.model
    def default_get(self, default_fields):
        res=super(PurchaseRequisition, self).default_get(default_fields)
        if 'picking_type_id' in res:
            del(res['picking_type_id'])
        return res
    
    @api.one
    def _compute_aaa_sel(self):
        if not self.account_analytic_id_sel:
            self.account_analytic_id_sel = self.account_analytic_id.id
        if not self.last_parent:
            self.last_parent = self.account_analytic_id.id
    
    @api.onchange('account_analytic_id_sel')
    def onchg_aanalytic_id(self):
        if self.account_analytic_id_sel:
            if self.account_analytic_id_sel.id < 0:
                self.account_analytic_id_sel=self.env['account.analytic.account'].browse(self.last_parent).parent_id
            if self.account_analytic_id_sel.x_type:
                self.last_parent=self.account_analytic_id_sel.id
                self.account_analytic_id_sel=None
            else:
                self.account_analytic_id=self.account_analytic_id_sel.id
                self.last_parent=self.account_analytic_id.parent_id
                
    @api.onchange('last_parent')
    def onchg_parent_id(self):
        if self.last_parent:
            #Se obtienen los registros los hijos del padre en forma de lista
            res_ids=self.env['account.analytic.account'].browse(self.last_parent).child_id.mapped('id')
            return {
                'domain': {
                    'account_analytic_id_sel': [('id','in',res_ids)],
                    }
                }

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"
            
    @api.one
    def _compute_aaa_sel(self):
        if not self.account_analytic_id_sel:
            self.account_analytic_id_sel = self.account_analytic_id.id
        if not self.last_parent:
            self.last_parent = self.account_analytic_id.id
    
    product_type = fields.Selection(related='product_id.type')
    account_analytic_id_sel = fields.Many2one('account.analytic.account', string='Analytic Account', compute='_compute_aaa_sel', 
         readonly=False)
    last_parent = fields.Integer(compute='_compute_aaa_sel', readonly=False, 
         default=lambda self: self.env['account.analytic.account'].search([('name','=','000 CPC')]).id)
    
    @api.onchange('account_analytic_id')
    def onchg_aanalytic(self):
        if self.account_analytic_id and not self.account_analytic_id_sel:
            self.account_analytic_id_sel=self.account_analytic_id
    
    @api.onchange('account_analytic_id_sel')
    def onchg_aanalytic_id(self):
        if self.account_analytic_id_sel:
            if self.account_analytic_id_sel.id < 0:
                self.account_analytic_id_sel=self.env['account.analytic.account'].browse(self.last_parent).parent_id
            if self.account_analytic_id_sel.x_type:
                self.last_parent=self.account_analytic_id_sel.id
                self.account_analytic_id_sel=None
            else:
                self.account_analytic_id=self.account_analytic_id_sel.id
                self.last_parent=self.account_analytic_id.parent_id
                
    @api.onchange('last_parent')
    def onchg_parent_id(self):
        if self.last_parent:
            #Se obtienen los registros los hijos del padre en forma de lista
            res_ids=self.env['account.analytic.account'].browse(self.last_parent).child_id.mapped('id')
            return {
                'domain': {
                    'account_analytic_id_sel': [('id','in',res_ids)],
                    }
                }
    #account_analytic_id = fields.Many2one('account.analytic.account', domain=[('x_type','=',False)])
    
    
    
