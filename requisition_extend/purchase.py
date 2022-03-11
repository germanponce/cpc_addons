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

class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit ='purchase.requisition'



    @api.onchange('order_count','purchase_ids')
    def onchange_purchase_ids_origin(self):
        if self.purchase_ids:
            origin =[str(x.name) for x in self.purchase_ids]
            self.origin = str(origin)



class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit ='purchase.order'


    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if res.requisition_id:
            if res.requisition_id.origin:
                res.requisition_id.origin = res.requisition_id.origin+", "+res.name
            else:
                res.requisition_id.origin = res.name
        return res