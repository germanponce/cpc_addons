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

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit ='purchase.order'

    ### Fincamiento  ### 
    @api.multi
    @api.depends('amount_total')
    def _search_best_price_evaluation(self):
        for purchase in self:
            if not purchase.fincamiento and not purchase.authorized and purchase.requisition_id:
                self.env.cr.execute("""
                    select amount_total 
                        from purchase_order where fincamiento = False
                        and authorized = False and
                        state in ('draft','sent','to approve')
                        and requisition_id = %s;

                    """,(purchase.requisition_id.id,))
                cr_res = self.env.cr.fetchall()
                price_list = [x[0] for x in cr_res]
                if price_list:
                    price_list.sort()
                    if purchase.amount_total <= price_list[0]:
                        purchase.best_price_evaluation_reference = True
                        self.env.cr.execute("""
                            update purchase_order set  best_price_evaluation_reference = False
                                where fincamiento = False and authorized = False and id != %s
                                and state in ('draft','sent','to approve')
                                and requisition_id = %s;
                            """,(purchase.id, purchase.requisition_id.id))
                    else:
                        purchase.best_price_evaluation_reference = False
                else:
                    purchase.best_price_evaluation_reference = False
            else:
                purchase.best_price_evaluation_reference = False

    ### Fincamiento  ### 
    @api.multi
    @api.depends('date_planned')
    def _search_date_planned_evaluation(self):
        for purchase in self:
            if not purchase.fincamiento and not purchase.authorized and purchase.requisition_id:
                self.env.cr.execute("""
                    select date_planned 
                        from purchase_order where fincamiento = False
                        and authorized = False
                        and state in ('draft','sent','to approve')
                        and requisition_id = %s;

                    """,(purchase.requisition_id.id,))
                cr_res = self.env.cr.fetchall()
                date_list = [x[0] for x in cr_res]
                if date_list:
                    date_list.sort()
                    if purchase.date_planned <= date_list[0]:
                        purchase.best_date_planned_evaluation_reference = True
                        self.env.cr.execute("""
                            update purchase_order set  best_date_planned_evaluation_reference = False
                                where fincamiento = False and authorized = False and id != %s
                                and state in ('draft','sent','to approve')
                                and requisition_id = %s;
                            """,(purchase.id, purchase.requisition_id.id))
                    else:
                        purchase.best_date_planned_evaluation_reference = False
                else:
                    purchase.best_date_planned_evaluation_reference = False
            else:
                purchase.best_date_planned_evaluation_reference = False

    ### Fincamiento  ### 
    best_price_evaluation_reference = fields.Boolean('Mejor Precio Fincado',  compute='_search_best_price_evaluation', readonly=True, store=True)

    best_date_planned_evaluation_reference = fields.Boolean('Mejor Fecha de Entrega',  compute='_search_date_planned_evaluation', readonly=True, store=True)

