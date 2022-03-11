# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MedicalPrescripionSelect(models.TransientModel):
    _name = "medical.prescription.select"
    _description = "Prescription report selection"
    
    @api.multi
    def button_half(self):
        return self.env['report'].get_action(self._context['active_ids'], 'hospital_management_prescription_sel.prescription_order_half_tmpt')
    
    def button_letter(self):
        return self.env['report'].get_action(self._context['active_ids'], 'hospital_management_prescription_sel.prescription_order_letter_tmpt')
