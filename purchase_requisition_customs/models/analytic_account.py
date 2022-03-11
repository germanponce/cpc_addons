# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        #Si el campo trae el contexto para ignorar el dominio de búsqueda
        if self.env.context.get('use_ignore_domain',False) and len(name):
            #VSGTN: ¿Es siempre el primer argumento el dominio?
            args=None
        return super(AccountAnalyticAccount,self).name_search(name,args,operator,limit)
