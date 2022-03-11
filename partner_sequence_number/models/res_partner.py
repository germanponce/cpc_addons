# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = "res.partner"
    
    #sequence = fields.Integer('Sequence', readonly=True, help="Used to order the views")
    sequence = fields.Integer('Sequence', help="Used to order the views")
    
    @api.model
    def create(self, vals):
        #if vals['supplier'] == True and vals['parent_id'] == False:
        #    vals['sequence'] = self.env.ref('partner_sequence_number.res_partner_seq_no').next_by_id()
        return super(Partner, self).create(vals)
