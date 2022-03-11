# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        #Se altera el método para permitir la inclusión del elemento que lleve al nivel superior
        res=[]
        #Si el campo trae el contexto asignado en la vista, se añade al principio la opción que permitirá su distinción
        if self.env.context.get('use_up_option',False) and name=='':
            limit-=1
            res.append((-1,'..'))
        #Se extiende el resultado con la respuesta del método original
        res.extend(super(AccountAnalyticAccount,self).name_search(name,args,operator,limit))
        return res