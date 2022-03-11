# -*- coding: utf-8 -*-

import models

def set_defaults(cr,registry):
    from odoo.api import Environment, SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.values'].set_default('sale.state.config', 'customer_template', env.ref('sale_cron_track.mail_state_template_customer_default').id)
    env['ir.values'].set_default('sale.state.config', 'agent_template', env.ref('sale_cron_track.mail_state_template_agent_default').id)
    env['ir.values'].set_default('sale.state.config', 'agent_late_template', env.ref('sale_cron_track.mail_state_template_agent_late_default').id)
    env['ir.values'].set_default('sale.state.config', 'days_notif', 5)
    env['ir.values'].set_default('sale.state.config', 'days_late', 10)
