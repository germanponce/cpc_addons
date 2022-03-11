# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
import pytz
from odoo import tools

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"
    
    product_uom_rel = fields.Many2one(related='product_id.uom_po_id')
