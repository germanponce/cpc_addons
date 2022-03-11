# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"
    
    return_reason = fields.Selection(
        [
            ('cred_doc','With Credit Document'),
            ('no_cred_doc','Without Credit Document'),
            ('reship','Reshipment')
        ],
        string='Return reason', 
        readonly=True, 
        help="Explanation about this picking at create time from return"
    )
