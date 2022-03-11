# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    @api.one
    @api.constrains('default_code')
    def _check_default_code_no_unique(self):
        if self.id:
            res = self.search([('default_code', '=',  self.default_code), ('default_code','!=',''), ('id','!=',self.id)])
            if len(res):
                raise ValueError(_('Error! The provided value for default_code in %s already exists') % (self.name))
        return