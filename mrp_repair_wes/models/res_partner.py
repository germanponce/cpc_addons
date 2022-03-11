# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'
    
    repair_partner = fields.Boolean(string='Is a Repairing Contact',
                               help="Check this box if this contact is a Repairing Contact. "
                               "If it's not checked, repair people will not see it for select on repair order.")