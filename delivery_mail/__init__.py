# -*- coding: utf-8 -*-

import models

def set_defaults(cr,registry):
    from odoo.api import Environment, SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.values'].set_default('delivery.mail.settings', 'customer_template', env.ref('delivery_mail.mail_delivery_template_customer_default').id)
    env['ir.values'].set_default('delivery.mail.settings', 'agent_template', env.ref('delivery_mail.mail_delivery_template_agent_default').id)
