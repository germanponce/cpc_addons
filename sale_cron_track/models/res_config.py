# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleStateConfig(models.TransientModel):
    _name = 'sale.state.config'
    _inherit = 'res.config.settings'
    
    days_notif = fields.Integer('First Notification Days', help='Days before first notification sending')
    days_late = fields.Integer('Late Notification Days', help='Days before late notification sending')
    customer_template = fields.Many2one('mail.template', string='Customer Delivery Template', 
                                 help='Specify Mail Template to use on customer notification.')
    agent_template = fields.Many2one('mail.template', string="Sales Agent Delivery Template", 
                                help='Specify Mail Template to use on sales agent notification.')
    agent_late_template = fields.Many2one('mail.template', string="Sales Agent Delivery Template", 
                                help='Specify Mail Template to use on sales agent notification.')
    
    @api.constrains('days_notif','days_late')
    def _check_valid_int(self):
        for record in self:
            if record.days_notif<1 or record.days_late<1:
                raise models.ValidationError(_('Days must be greather than 0'))
    
    @api.multi
    def set_customer_template_defaults(self):
        res = self.env['ir.values'].sudo().set_default('sale.state.config', 'customer_template', self.customer_template.id)
        return res
    
    @api.multi
    def set_agent_template_defaults(self):
        res = self.env['ir.values'].sudo().set_default('sale.state.config', 'agent_template', self.agent_template.id)
        return res
    
    @api.multi
    def set_agent_late_template_defaults(self):
        res = self.env['ir.values'].sudo().set_default('sale.state.config', 'agent_late_template', self.agent_late_template.id)
        return res
    
    @api.multi
    def set_days_notif_defaults(self):
        res = self.env['ir.values'].sudo().set_default('sale.state.config', 'days_notif', self.days_notif)
        return res
    
    @api.multi
    def set_days_late_defaults(self):
        res = self.env['ir.values'].sudo().set_default('sale.state.config', 'days_late', self.days_late)
        return res
