# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MailDeliveryConfig(models.TransientModel):
    _name = 'delivery.mail.settings'
    _inherit = 'res.config.settings'
    
    customer_template = fields.Many2one('mail.template', string='Customer Delivery Template', 
                                 help='Specify Mail Template to use on customer notification.')
    agent_template = fields.Many2one('mail.template', string="Sales Agent Delivery Template", 
                                help='Specify Mail Template to use on sales agent notification.')
    
    @api.multi
    def set_customer_template_defaults(self):
        res = self.env['ir.values'].sudo().set_default('delivery.mail.settings', 'customer_template', self.customer_template.id)
        return res
    
    @api.multi
    def set_agent_template_defaults(self):
        res = self.env['ir.values'].sudo().set_default('delivery.mail.settings', 'agent_template', self.agent_template.id)
        return res
