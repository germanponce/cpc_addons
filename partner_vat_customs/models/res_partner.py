# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = "res.partner"
    
    @api.one
    @api.constrains('vat')
    def _check_vat_no_unique(self):
        if self.id:
            res = self.search([('supplier','=','True'), ('parent_id','=', 'False'), ('vat', '=',  self.vat), ('id','!=',self.id)])
            if len(res):
                raise ValueError(_('Error! The provided value for VAT in %s already exists') % (self.name))
        return
