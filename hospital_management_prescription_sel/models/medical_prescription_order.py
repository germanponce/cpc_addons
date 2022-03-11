# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class medical_prescription_order(models.Model):
    _inherit = "medical.prescription.order"
    
    @api.multi
    def prescription_report(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'medical.prescription.select',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }
    