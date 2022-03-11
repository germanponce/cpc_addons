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


# class StockPicking(models.Model):
#     _name = 'stock.picking'
#     _inherit ='stock.picking'

#     @api.model
#     def create(self, vals):
#         res = super(StockPicking, self).create(vals)
#         return res


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit ='purchase.order'

    local_purchase = fields.Boolean('Compra Local (1 paso)')

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if res.requisition_id:
            if res.requisition_id.local_purchase:
                res.local_purchase = True
        return res


    @api.onchange('requisition_id')
    def onchange_requisition_local(self):
        if self.requisition_id:
            self.local_purchase = self.requisition_id.local_purchase

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        if self.local_purchase == False:
            if self.dest_address_id:
                return self.dest_address_id.property_stock_customer.id
            return self.picking_type_id.default_location_dest_id.id
        else:
            if self.dest_address_id:
                return self.dest_address_id.property_stock_customer.id
            else:
                return self.picking_type_id.warehouse_id.lot_stock_id.id

class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit ='purchase.requisition'

    local_purchase = fields.Boolean('Compra Local (1 paso)')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    local_purchase = fields.Boolean('Compra Local (1 paso)', related="purchase_id.local_purchase")