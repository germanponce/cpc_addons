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



class ResUsers(models.Model):
    _name = 'res.users'
    _inherit ='res.users'

    warehouse_ids = fields.Many2many('stock.warehouse','users_wareouses_rel','user_id','warehouse_id','Almacenes')

    product_category_ids = fields.Many2many('product.category','users_category_rel','user_id','category_id','Categorias de Productos')


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit ='purchase.requisition'

    @api.onchange('name','user_id')
    def onchange_purchase_req_move_type(self):
        uid = self._uid
        user = self.env['res.users'].browse(uid)
        warehouse_ids = [x.id for x in user.warehouse_ids]

        picking_type_obj = self.env['stock.picking.type']
        picking_type_ids = picking_type_obj.search([('warehouse_id','in',tuple(warehouse_ids))])
        
        picking_type_ids = [x.id for x in picking_type_ids]
        if user.warehouse_ids:
            return {'domain': {'picking_type_id':[('warehouse_id','in',warehouse_ids),('code','=','incoming')]}}
        #     return {'domain': {'picking_type_id':[('warehouse_id','child_of',warehouse_ids)]}}
        # else:
        #     return {'domain': {'picking_type_id':[('id','in',())]}}
        # # return {'domain': {'location_id':[('warehouse_id','in',warehouse_ids)],'location_dest_id':[('warehouse_id','in',warehouse_ids)]}}

class PurchaseRequisitionLine(models.Model):
    _name = 'purchase.requisition.line'
    _inherit ='purchase.requisition.line'

    domain_category_user = fields.Boolean('Activar Booleano', default=True)

    @api.onchange('product_id', 'domain_category_user','requisition_id')
    def onchange_purchase_line_return_domain(self):
        uid = self._uid
        user = self.env['res.users'].browse(uid)
        if self.requisition_id.picking_type_id.warehouse_id.product_category_ids:
            category_ids = [x.id for x in self.requisition_id.picking_type_id.warehouse_id.product_category_ids]
            return {'domain': {'product_id':[('categ_id','child_of',category_ids)]}}
        else:
            if user.product_category_ids:
                category_ids = [x.id for x in user.product_category_ids]
                return {'domain': {'product_id':[('categ_id','child_of',category_ids)]}}

        # product_obj = self.env['product.product']
        # product_ids = product_obj.search([('categ_id','in',tuple(category_ids))])
        
        # product_ids = [x.id for x in product_ids]
        # if product_ids:
        #     return {'domain': {'product_id':[('id','in',product_ids)]}}
        # else:
        #     product_ids = product_obj.search([])
        #     return {'domain': {'product_id':[('id','in',())]}}
        # return {'domain': {'location_id':[('warehouse_id','in',category_ids)],'location_dest_id':[('warehouse_id','in',warehouse_ids)]}}

class StockMove(models.Model):
    _name = 'stock.move'
    _inherit ='stock.move'

    domain_category_user = fields.Boolean('Activar Booleano', default=True)

    @api.onchange('product_id', 'domain_category_user','picking_id')
    def onchange_purchase_line_return_domain(self):
        uid = self._uid
        user = self.env['res.users'].browse(uid)
        if self.picking_id:
            if self.picking_id.picking_type_id.warehouse_id.product_category_ids:
                category_ids = [x.id for x in self.picking_id.picking_type_id.warehouse_id.product_category_ids]
                return {'domain': {'product_id':[('categ_id','child_of',category_ids)]}}
            else:
                if user.product_category_ids:
                    category_ids = [x.id for x in user.product_category_ids]
                    return {'domain': {'product_id':[('categ_id','child_of',category_ids)]}}
        else:
            if user.product_category_ids:
                category_ids = [x.id for x in user.product_category_ids]
                return {'domain': {'product_id':[('categ_id','child_of',category_ids)]}}

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit ='purchase.order'

    @api.onchange('date_order','picking_type_id','partner_id')
    def onchange_purchase_req_move_type(self):
        uid = self._uid
        user = self.env['res.users'].browse(uid)
        warehouse_ids = [x.id for x in user.warehouse_ids]

        picking_type_obj = self.env['stock.picking.type']
        picking_type_ids = picking_type_obj.search([('warehouse_id','in',tuple(warehouse_ids))])
        
        picking_type_ids = [x.id for x in picking_type_ids]
        if user.warehouse_ids:
            return {'domain': {'picking_type_id':[('warehouse_id','in',warehouse_ids),('code','=','incoming')]}}

        #     return {'domain': {'picking_type_id':[('warehouse_id','child_of',warehouse_ids)]}}
        # if picking_type_ids:
        #     return {'domain': {'picking_type_id':[('id','in',picking_type_ids),('code','=','incoming')]}}
        # else:
        #     return {'domain': {'picking_type_id':[('id','in',())]}}
        # # return {'domain': {'location_id':[('warehouse_id','in',warehouse_ids)],'location_dest_id':[('warehouse_id','in',warehouse_ids)]}}

class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit ='purchase.order.line'

    domain_category_user = fields.Boolean('Activar Booleano', default=True)

    @api.onchange('product_id', 'domain_category_user')
    def onchange_purchase_line_return_domain(self):
        uid = self._uid
        user = self.env['res.users'].browse(uid)
        if user.product_category_ids:
            category_ids = [x.id for x in user.product_category_ids]

            return {'domain': {'product_id':[('categ_id','child_of',category_ids)]}}

            # product_obj = self.env['product.product']
            # product_ids = product_obj.search([('categ_id','in',tuple(category_ids))])
            
            # product_ids = [x.id for x in product_ids]
            # if product_ids:
            #     return {'domain': {'product_id':[('id','in',product_ids)]}}
            # else:
            #     return {'domain': {'product_id':[('id','in',())]}}
            # # return {'domain': {'location_id':[('warehouse_id','in',category_ids)],'location_dest_id':[('warehouse_id','in',warehouse_ids)]}}


class StockWarehouse(models.Model):
    _name = 'stock.warehouse'
    _inherit ='stock.warehouse'

    product_category_ids = fields.Many2many('product.category','warehouse_category_rel','warehouse_id','category_id','Categorias de Productos')
