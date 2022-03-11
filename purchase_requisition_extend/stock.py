# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


from openerp import models, fields, api, _
from datetime import time, datetime
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import time
from odoo.tools.translate import _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    requisition_id = fields.Many2one('purchase.requisition', string='Latest Requisition')

    @api.multi
    def make_po(self):
        context = self._context
        Requisition = self.env['purchase.requisition']
        RequisitionLine = self.env['purchase.requisition.line']
        procurements = self.env['procurement.order']
        Warehouse = self.env['stock.warehouse']
        res = []
        for procurement in self:
            if procurement.product_id.purchase_requisition == 'tenders':
                warehouse_id = Warehouse.search([('company_id', '=', procurement.company_id.id)], limit=1).id
                requisition_prev = Requisition.search([('state','=','draft'),('procurement_id','!=',False),('warehouse_id','=',procurement.warehouse_id.id)])
                if requisition_prev:
                    requisition_line_id = RequisitionLine.create({
                        'product_id': procurement.product_id.id,
                        'product_uom_id': procurement.product_uom.id,
                        'product_qty': procurement.product_qty,
                        'procurement_id': procurement.id,
                        'requisition_id': requisition_prev[0].id,
                        })
                    requisition_id = requisition_prev[0]
                else:
                    requisition_id = Requisition.create({
                        'origin': procurement.origin,
                        'date_end': procurement.date_planned,
                        'warehouse_id': warehouse_id,
                        'company_id': procurement.company_id.id,
                        'procurement_id': procurement.id,
                        'picking_type_id': procurement.rule_id.picking_type_id.id,
                        'line_ids': [(0, 0, {
                            'product_id': procurement.product_id.id,
                            'product_uom_id': procurement.product_uom.id,
                            'product_qty': procurement.product_qty
                        })],
                    })
                procurement.message_post(body=_("Purchase Requisition created"))
                requisition_id.message_post_with_view('mail.message_origin_link',
                    values={'self': requisition_id, 'origin': procurement},
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
                procurement.requisition_id = requisition_id
                procurements += procurement
                res += [procurement.id]
        set_others = self - procurements
        if set_others:
            res += super(ProcurementOrder, set_others).make_po()
        return res


