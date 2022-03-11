# -*- coding: utf-8 -*-

from odoo.addons.web.controllers.main import Action
from odoo.http import request
from odoo import http

class Action(Action):
    @http.route('/web/action/load', type='json', auth="user")
    def load(self, action_id, additional_context=None):
        res = super(Action,self).load(action_id,additional_context)
        if 'context_origin_action' in request.env.context and request.env.context['context_origin_action']:
            res['context']={'origin_action':request.env.context['params']['action']}
        return res
