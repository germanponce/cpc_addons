# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductCategory(models.Model):
    _inherit = "product.category"
    
    repairable_prod = fields.Boolean(string='Is a Repairable Product',
                               help="Check this box if this product is Repairable. "
                               "If it's not checked, repair people will not see it for select on repair order.")
    part_prod = fields.Boolean(string='Is a Part Product',
                               help="Check this box if this product is a Part for repairing. "
                               "If it's not checked, repair people will not see it for select on repair order.")
    
class product_template(models.Model):
    _inherit ='product.template'
    
    @api.model
    def _domain_categ_id(self):
        context = self._context
        if 'from_repair_rep' in context:
            return "[('repairable_prod','=',True),('type','=','normal')]"
        elif 'from_repair_part' in context:
            return "[('part_prod','=',True),('type','=','normal')]"
        else:
            return "[('type','=','normal')]"
        
    def _get_default_category_id(self):
        context = self._context
        if 'from_repair_rep' in context or 'from_repair_part' in context:
            return 
        else:
            return super(product_template,self)._get_default_category_id()
    
    is_repairable = fields.Boolean(related='categ_id.repairable_prod')
    is_hdd = fields.Boolean(string='Is a Hard Drive',
                               help="Check this box if this product is a Hard Drive. "
                               "If it's not checked, repair people will not fill important data.")
    
    categ_id = fields.Many2one(domain=_domain_categ_id, default=_get_default_category_id)
    