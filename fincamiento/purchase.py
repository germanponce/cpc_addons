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


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit ='res.partner'

    ### Fincamiento ### 
    @api.multi
    def _get_products_count(self):
        for partner in self:
            self.env.cr.execute("""
                select product_tmpl_id from product_supplierinfo where name=%s
                    and fincamiento = True;
                """,(partner.id,))
            cr_res = self.env.cr.fetchall()
            product_list = [x[0] for x in cr_res]
            if product_list:
                partner.product_fincados_count = len(product_list)
            else:
                partner.product_fincados_count = 0

    ### Fincamiento  ### 
    fincamiento_automatic = fields.Boolean('Fincamiento Automatico')
    product_fincados_count = fields.Integer(string='Numero Productos Fincados', compute='_get_products_count', readonly=True)
    fincamiento_reference = fields.Many2one('fincamiento.reference', 'Referencia de Fincamiento')

    ### Autorizado  ### 
    authorized = fields.Boolean('Autorizado')

    ### Fincamiento  ### 
    @api.multi
    def action_view_products_fincados(self):
        for partner in self:
            self.env.cr.execute("""
                    select product_tmpl_id from product_supplierinfo where name=%s and fincamiento = True;
                    """,(partner.id,))
            cr_res = self.env.cr.fetchall()
            product_list = [x[0] for x in cr_res]

            if len(product_list) > 1:
                return {
                    'domain': [('id', 'in', product_list)],
                    'name': _('Productos  para %s' % self.name),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'product.template',
                    'type': 'ir.actions.act_window'
                    }
            else:
                return {
                    'name': _('Productos Fincados para %s' % self.name),
                    'view_mode': 'form',
                    'res_model': 'product.template',
                    'type': 'ir.actions.act_window',
                    'res_id': product_list[0],
                    }


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit ='purchase.order'

    ### Fincamiento  ### 
    @api.multi
    @api.depends('amount_total', 'fincamiento_reference')
    def _search_best_price(self):
        for purchase in self:
            if purchase.fincamiento and purchase.fincamiento_reference:
                self.env.cr.execute("""
                    select amount_total 
                        from purchase_order where fincamiento_reference = %s
                        and state in ('draft','sent','to approve');

                    """,(purchase.fincamiento_reference.id,))
                cr_res = self.env.cr.fetchall()
                price_list = [x[0] for x in cr_res]
                if price_list:
                    price_list.sort()
                    if purchase.amount_total <= price_list[0]:
                        purchase.best_price_fincado_reference = True
                        self.env.cr.execute("""
                            update purchase_order set  best_price_fincado_reference = False
                                where fincamiento_reference = %s and id != %s
                                and state in ('draft','sent','to approve');
                            """,(purchase.fincamiento_reference.id, purchase.id, ))
                    else:
                        purchase.best_price_fincado_reference = False
                else:
                    purchase.best_price_fincado_reference = False
            else:
                purchase.best_price_fincado_reference = False

    ### Fincamiento  ### 
    @api.multi
    @api.depends('date_planned', 'fincamiento_reference')
    def _search_date_planned(self):
        for purchase in self:
            if purchase.fincamiento and purchase.fincamiento_reference:
                self.env.cr.execute("""
                    select date_planned 
                        from purchase_order where fincamiento_reference = %s
                        and state in ('draft','sent','to approve');

                    """,(purchase.fincamiento_reference.id,))
                cr_res = self.env.cr.fetchall()
                date_list = [x[0] for x in cr_res]
                if date_list:
                    date_list.sort()
                    if purchase.date_planned <= date_list[0]:
                        purchase.best_price_date_planned_reference = True
                        self.env.cr.execute("""
                            update purchase_order set  best_price_date_planned_reference = False
                                where fincamiento_reference = %s and id != %s
                                and state in ('draft','sent','to approve');
                            """,(purchase.fincamiento_reference.id, purchase.id, ))
                    else:
                        purchase.best_price_date_planned_reference = False
                else:
                    purchase.best_price_date_planned_reference = False
            else:
                purchase.best_price_date_planned_reference = False

    ### Fincamiento  ### 
    fincamiento = fields.Boolean('Fincamiento')
    fincamiento_reference = fields.Many2one('fincamiento.reference', 'Referencia de Fincamiento')

    best_price_fincado_reference = fields.Boolean('Mejor Precio Fincado',  compute='_search_best_price', readonly=True, store=True)

    best_price_date_planned_reference = fields.Boolean('Mejor Fecha de Entrega',  compute='_search_date_planned', readonly=True, store=True)

    ### Autorizado  ### 
    authorized = fields.Boolean('Autorizado')

    ### Fincamiento  ### 
    @api.model
    def default_get(self, default_fields):

        context = self._context
        if 'fincamiento' in context:
            fincamiento = context['fincamiento']
            if fincamiento:
                contextual_self = self.with_context(default_fincamiento=fincamiento)
                return super(PurchaseOrder, contextual_self).default_get(default_fields)
            else:
                return super(PurchaseOrder, self).default_get(default_fields)
        else:
            return super(PurchaseOrder, self).default_get(default_fields)

    ### Fincamiento  ### 
    @api.onchange('partner_id')
    def onchange_partner_fincamiento(self):
        if self.partner_id:
            if self.partner_id.fincamiento_reference:
                self.fincamiento_reference = self.partner_id.fincamiento_reference.id
    

class ProductSupplierinfo(models.Model):
    _name = 'product.supplierinfo'
    _inherit ='product.supplierinfo'

    ### Fincamiento  ### 
    @api.multi
    @api.depends('name')
    def _compute_field_fincamiento(self):
        for rec in self:
            if rec.name:
                rec.fincamiento = rec.name.fincamiento_automatic

    ### Autorizado  ### 
    @api.multi
    @api.depends('name')
    def _compute_field_authorized(self):
        for rec in self:
            if rec.name:
                rec.authorized = rec.name.authorized


    ### Fincamiento  ### 
    fincamiento = fields.Boolean('Fincada', compute='_compute_field_fincamiento', readonly=True, store=True)

    ### Autorizado  ### 
    authorized = fields.Boolean('Autorizada', compute='_compute_field_authorized', readonly=True, store=True)


    # @api.onchange('name')
    # def onchange_partner_fincamiento(self):
    #     if self.name:
    #         self.fincamiento = True
    

    @api.constrains('product_id','product_tmpl_id','name')
    def _constrain_pricelist_by_partner(self):
        if self.name and self.product_id:  
            other_ids = self.search([('id','!=',self.id),('name','=',self.name.id),('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
            if other_ids:
                raise UserError("Error!\nYa existe una Tarifa de este Proveedor en el Producto.")
        if self.name and self.product_tmpl_id:  
            other_ids = self.search([('id','!=',self.id),('name','=',self.name.id),('product_tmpl_id','=',self.product_tmpl_id.id)])
            if other_ids:
                raise UserError("Error!\nYa existe una Tarifa de este Proveedor en el Producto.")

        return True

    @api.constrains('fincamiento','authorized','product_tmpl_id')
    def _constrain_by_product_fincamiento_authorized(self):
        if self.authorized:
            other_ids = self.search([('id','!=',self.id),
                                     ('product_tmpl_id','=',self.product_tmpl_id.id),
                                     ('fincamiento','=',True),
                                    ])
            if other_ids:
                raise UserError("Error!\nYa existe una Tarifa con un Proveedor Fincado para este Producto.")
            else:
                other_ids = self.search([('id','!=',self.id),
                                         ('product_tmpl_id','=',self.product_tmpl_id.id),
                                         ('authorized','=',True),
                                        ])
                if other_ids:
                    raise UserError("Error!\nYa existe una Tarifa con un Proveedor Autorizado para este Producto.")

        if self.fincamiento:
            other_ids = self.search([('id','!=',self.id),
                                     ('product_tmpl_id','=',self.product_tmpl_id.id),
                                     ('authorized','=',True),
                                    ])
            if other_ids:
                raise UserError("Error!\nYa existe una Tarifa con un Proveedor Autorizado para este Producto.")
            else:
                other_ids = self.search([('id','!=',self.id),
                                         ('product_tmpl_id','=',self.product_tmpl_id.id),
                                         ('fincamiento','=',True),
                                        ])
                if other_ids:
                    raise UserError("Error!\nYa existe una Tarifa con un Proveedor Fincado para este Producto.")


        return True
    

class PurchaseRequisitionLine(models.Model):
    _name = 'purchase.requisition.line'
    _inherit ='purchase.requisition.line'

    ### Fincamiento  ### 
    @api.multi
    @api.depends('product_id')
    def _compute_field_fincamiento(self):
        for rec in self:
            if rec.product_id:
                for supp in rec.product_id.seller_ids:
                    if supp.fincamiento:
                        rec.fincamiento = True
                        rec.supplier_id = supp.name.id
                        break

    ### Autorizado  ### 
    @api.multi
    @api.depends('product_id')
    def _compute_field_authorized(self):
        for rec in self:
            if rec.product_id:
                for supp in rec.product_id.seller_ids:
                    if supp.authorized:
                        rec.authorized = True
                        rec.authorized_supplier_id = supp.name.id
                        break


    ### Fincamiento  ### 
    fincamiento = fields.Boolean('Fincado', compute='_compute_field_fincamiento', readonly=True, store=True)
    supplier_id = fields.Many2one('res.partner', 'Proveedor Fincado', compute='_compute_field_fincamiento', readonly=True, store=True)
    
    ### Autorizado ###
    authorized_supplier_id = fields.Many2one('res.partner', 'Proveedor Autorizado', compute='_compute_field_authorized', readonly=True, store=True)
    authorized = fields.Boolean('Autorizado', compute='_compute_field_authorized', readonly=True, store=True)


    @api.onchange('product_id', 'supplier_id','authorized_supplier_id')
    def onchange_price_supplier_info(self):
        supp_obj = self.env["product.supplierinfo"]
        if self.product_id and self.supplier_id:
            supp_id = supp_obj.search([('name','=',self.supplier_id.id),('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
            if supp_id:
                self.price_unit = supp_id[0].price
        if self.product_id and self.authorized_supplier_id:
            supp_id = supp_obj.search([('name','=',self.authorized_supplier_id.id),('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
            if supp_id:
                self.price_unit = supp_id[0].price

class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit ='purchase.requisition'

    ### Fincamiento  ### 
    @api.multi
    @api.depends('line_ids')
    def _compute_field_fincamiento(self):
        for rec in self:
            for detail in rec.line_ids:
                if detail.fincamiento:
                    rec.have_fincamiento = True
                    break

    ### Autorizado  ### 
    @api.multi
    @api.depends('line_ids')
    def _compute_field_authorized(self):
        for rec in self:
            for detail in rec.line_ids:
                if detail.authorized:
                    rec.have_authorization = True
                    break

    ### Autorizado  ### 
    @api.multi
    @api.depends('line_ids')
    def _compute_field_authorized_fincado(self):
        for rec in self:
            for detail in rec.line_ids:
                if detail.authorized:
                    rec.show_wizard_fincado_authorized = True
                    break
                elif detail.fincamiento:
                    rec.show_wizard_fincado_authorized = True
                    break

    ### Fincamiento  ### 
    have_fincamiento = fields.Boolean('Tiene Fincados', compute='_compute_field_fincamiento', readonly=True, store=True)

    ### Autorizado  ### 
    have_authorization = fields.Boolean('Tiene Autorizacion', compute='_compute_field_authorized', readonly=True, store=True)

    show_wizard_fincado_authorized = fields.Boolean('Tiene Autorizacion/Fincamiento', compute='_compute_field_authorized_fincado', readonly=True, store=True)

    ### Si tiene fincamientos, desaparecer el Boton de Nueva Cotizacion por un nuevo wizard


class FincamientoReference(models.Model):
    _name = 'fincamiento.reference'
    _description = 'Este modelo permite controlar los procesos de Fincamiento'
    
    ### Fincamiento  ### 
    name = fields.Char('Referencia', size=128, required=True)

    _order = 'name' 

    ### Fincamiento  ### 
    @api.multi
    def cancel_quotations_fincadas(self):
        for rec in self:
            purchase_obj = self.env['purchase.order']
            purchase_ids = purchase_obj.search([('fincamiento','=',True),('state','in',('draft','sent','to approve')),('fincamiento_reference','=',rec.id)])
            for purchase in purchase_ids:
                purchase.button_cancel()

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _("El Registro debe ser Unico.")),
    ]
    
    
class PurchaseRequisitionFincamientoOrder(models.TransientModel):
    _name = 'purchase.requisition.fincamiento.order'
    _description = 'Creacion de Ordenes a partir de Fincamientos'


    def _get_vendor(self):
        active_ids = self._context['active_ids']

        for requisition in self.env['purchase.requisition'].browse(active_ids):
            if requisition.vendor_id:
                return requisition.vendor_id.id
            else:
                return False
    ### Fincamiento  ### 
    fincados = fields.Boolean('Fincados')
    no_fincados = fields.Boolean('No Fincados')
    all_products = fields.Boolean('Todos')

    make_selector = fields.Selection([
        ('fincados','Fincados'),
        ('authorized','Autorizados'),
        ('no_fincados','No Fincados y no Autorizados'),
        ('all_products','Todos'),
        ], 'Prespuestos para', default='fincados')
    supplier_id = fields.Many2one('res.partner','Proveedor', default=_get_vendor)


    ### Fincamiento  ### 
    @api.multi
    def make_orders(self):
        active_ids = self._context['active_ids']
        requisition_line = self.env['purchase.requisition.line']
        purchase_obj = self.env['purchase.order']
        purchase_list = []
        if not self.make_selector:
            raise UserError(_("Error!\nDebes seleccionar al menos una opción para la creación de Presupuestos."))
        for requisition in self.env['purchase.requisition'].browse(active_ids):
            if self.make_selector == 'fincados':
                self.env.cr.execute("""
                    select supplier_id from purchase_requisition_line
                        where requisition_id = %s and fincamiento=True
                        group by supplier_id;
                    """,(requisition.id,))
                cr_res = self.env.cr.fetchall()
                supplier_list = [x[0] for x in cr_res]
                if supplier_list:
                    for supplier in supplier_list:
                        requisition_line_records = requisition_line.search([('requisition_id','=',requisition.id),('supplier_id','=',supplier),('fincamiento','=',True)])
                        quotation_lines = []
                        for req_line in requisition_line_records:
                            partner = self.env['res.partner'].browse(supplier)

                            currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

                            payment_term = partner.property_supplier_payment_term_id

                            product_lang = req_line.product_id.with_context({
                                'lang': partner.lang,
                                'partner_id': partner.id,
                            })
                            name = product_lang.display_name
                            if product_lang.description_purchase:
                                name += '\n' + product_lang.description_purchase

                            # Compute quantity and price_unit
                            if requisition.type_id.quantity_copy != 'copy':
                                product_qty = 0
                                price_unit = req_line.price_unit
                            elif req_line.product_uom_id != req_line.product_id.uom_po_id:
                                product_qty = req_line.product_uom_id._compute_quantity(req_line.product_qty, req_line.product_id.uom_po_id)
                                price_unit = req_line.product_uom_id._compute_price(req_line.price_unit, req_line.product_id.uom_po_id)
                            else:
                                product_qty = req_line.product_qty
                                price_unit = req_line.price_unit

                            # Compute price_unit in appropriate currency
                            if requisition.company_id.currency_id != currency:
                                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

                            FiscalPosition = self.env['account.fiscal.position']
                            fpos = FiscalPosition.get_fiscal_position(partner.id)
                            fpos = FiscalPosition.browse(fpos)

                            # Compute taxes
                            if fpos:
                                taxes_ids = fpos.map_tax(req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
                            else:
                                taxes_ids = req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

                            xval = (0,0,{
                                'name': name,
                                'product_id': req_line.product_id.id,
                                'product_uom': req_line.product_uom_id.id,
                                'product_qty': req_line.product_qty,
                                'price_unit': price_unit,
                                'taxes_id': [(6, 0, taxes_ids)],
                                'date_planned': requisition.schedule_date or fields.Date.today(),
                                'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                                'account_analytic_id': req_line.account_analytic_id.id,

                                })
                            quotation_lines.append(xval)

                            purchase_vals = {
                                'payment_term' : partner.property_supplier_payment_term_id,
                                'currency' : partner.property_purchase_currency_id or requisition.company_id.currency_id,
                                'partner_id' : partner.id,
                                'fiscal_position_id' : fpos.id,
                                'payment_term_id' : payment_term.id,
                                'company_id' : requisition.company_id.id,
                                'currency_id' : currency.id,
                                'origin' : requisition.name,
                                'partner_ref' : requisition.name,
                                'notes' : requisition.description,
                                'date_order' : requisition.date_end or fields.Datetime.now(),
                                'picking_type_id' : requisition.picking_type_id.id,
                                'order_line':quotation_lines,
                                'fincamiento': True,
                                'fincamiento_reference': partner.fincamiento_reference.id,
                                'requisition_id': requisition.id,
                            }
                            ### Buscando un Pedido repetido
                            purchase_prev_id = purchase_obj.search([('partner_id','=',supplier),('requisition_id','=',requisition.id),('fincamiento_reference','=',partner.fincamiento_reference.id),('state','in',('to approve','purchase'))])
                            if purchase_prev_id:
                                raise UserError(_("Error!\nYa se tiene un Pedido Fincado para el Proveedor %s" % partner.name))
                            
                            purchase_id = purchase_obj.create(purchase_vals)
                            purchase_id.sudo().button_confirm()
                            purchase_id.sudo().button_approve()
                            purchase_list.append(purchase_id.id)
                return {
                    'domain': [('id', 'in', purchase_list)],
                    'name': _('Presupuestos Fincados para %s' % requisition.name),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window'
                    }

            elif self.make_selector == 'authorized':
                self.env.cr.execute("""
                    select authorized_supplier_id from purchase_requisition_line
                        where requisition_id = %s and authorized=True
                        group by authorized_supplier_id;
                    """,(requisition.id,))
                cr_res = self.env.cr.fetchall()
                supplier_list = [x[0] for x in cr_res]

                if supplier_list:
                    for supplier in supplier_list:
                        requisition_line_records = requisition_line.search([('requisition_id','=',requisition.id),('authorized_supplier_id','=',supplier),('authorized','=',True)])
                        quotation_lines = []
                        for req_line in requisition_line_records:
                            partner = self.env['res.partner'].browse(supplier)

                            currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

                            payment_term = partner.property_supplier_payment_term_id

                            product_lang = req_line.product_id.with_context({
                                'lang': partner.lang,
                                'partner_id': partner.id,
                            })
                            name = product_lang.display_name
                            if product_lang.description_purchase:
                                name += '\n' + product_lang.description_purchase

                            # Compute quantity and price_unit
                            if requisition.type_id.quantity_copy != 'copy':
                                product_qty = 0
                                price_unit = req_line.price_unit
                            elif req_line.product_uom_id != req_line.product_id.uom_po_id:
                                product_qty = req_line.product_uom_id._compute_quantity(req_line.product_qty, req_line.product_id.uom_po_id)
                                price_unit = req_line.product_uom_id._compute_price(req_line.price_unit, req_line.product_id.uom_po_id)
                            else:
                                product_qty = req_line.product_qty
                                price_unit = req_line.price_unit

                            # Compute price_unit in appropriate currency
                            if requisition.company_id.currency_id != currency:
                                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

                            FiscalPosition = self.env['account.fiscal.position']
                            fpos = FiscalPosition.get_fiscal_position(partner.id)
                            fpos = FiscalPosition.browse(fpos)

                            # Compute taxes
                            if fpos:
                                taxes_ids = fpos.map_tax(req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
                            else:
                                taxes_ids = req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

                            xval = (0,0,{
                                'name': name,
                                'product_id': req_line.product_id.id,
                                'product_uom': req_line.product_uom_id.id,
                                'product_qty': req_line.product_qty,
                                'price_unit': price_unit,
                                'taxes_id': [(6, 0, taxes_ids)],
                                'date_planned': requisition.schedule_date or fields.Date.today(),
                                'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                                'account_analytic_id': req_line.account_analytic_id.id,

                                })
                            quotation_lines.append(xval)

                            purchase_vals = {
                                'payment_term' : partner.property_supplier_payment_term_id,
                                'currency' : partner.property_purchase_currency_id or requisition.company_id.currency_id,
                                'partner_id' : partner.id,
                                'fiscal_position_id' : fpos.id,
                                'payment_term_id' : payment_term.id,
                                'company_id' : requisition.company_id.id,
                                'currency_id' : currency.id,
                                'origin' : requisition.name,
                                'partner_ref' : requisition.name,
                                'notes' : requisition.description,
                                'date_order' : requisition.date_end or fields.Datetime.now(),
                                'picking_type_id' : requisition.picking_type_id.id,
                                'order_line':quotation_lines,
                                'fincamiento': False,
                                'fincamiento_reference': False,
                                'authorized': True,
                                'requisition_id': requisition.id,
                            }
                            ### Buscando un Pedido repetido
                            purchase_prev_id = purchase_obj.search([('partner_id','=',supplier),('requisition_id','=',requisition.id),('state','not in',('done','cancel'))])
                            if purchase_prev_id:
                                raise UserError(_("Error!\nYa se tiene un Pedido Autorizado para el Proveedor %s" % partner.name))
                            
                            purchase_id = purchase_obj.create(purchase_vals)
                            # purchase_id.sudo().button_confirm()
                            # purchase_id.sudo().button_approve()
                            purchase_list.append(purchase_id.id)
                return {
                    'domain': [('id', 'in', purchase_list)],
                    'name': _('Presupuestos Autorizados para %s' % requisition.name),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window'
                    }

            elif self.make_selector == 'no_fincados':
                requisition_line_records = requisition_line.search([('requisition_id','=',requisition.id),('supplier_id','=',False),('fincamiento','=',False),('authorized','=',False)])
                quotation_lines = []
                for req_line in requisition_line_records:
                    partner = self.supplier_id

                    currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

                    payment_term = partner.property_supplier_payment_term_id

                    product_lang = req_line.product_id.with_context({
                        'lang': partner.lang,
                        'partner_id': partner.id,
                    })
                    name = product_lang.display_name
                    if product_lang.description_purchase:
                        name += '\n' + product_lang.description_purchase

                    # Compute quantity and price_unit
                    if requisition.type_id.quantity_copy != 'copy':
                        product_qty = 0
                        price_unit = req_line.price_unit
                    elif req_line.product_uom_id != req_line.product_id.uom_po_id:
                        product_qty = req_line.product_uom_id._compute_quantity(req_line.product_qty, req_line.product_id.uom_po_id)
                        price_unit = req_line.product_uom_id._compute_price(req_line.price_unit, req_line.product_id.uom_po_id)
                    else:
                        product_qty = req_line.product_qty
                        price_unit = req_line.price_unit

                    # Compute price_unit in appropriate currency
                    if requisition.company_id.currency_id != currency:
                        price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

                    FiscalPosition = self.env['account.fiscal.position']
                    fpos = FiscalPosition.get_fiscal_position(partner.id)
                    fpos = FiscalPosition.browse(fpos)

                    # Compute taxes
                    if fpos:
                        taxes_ids = fpos.map_tax(req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
                    else:
                        taxes_ids = req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

                    xval = (0,0,{
                        'name': name,
                        'product_id': req_line.product_id.id,
                        'product_uom': req_line.product_uom_id.id,
                        'product_qty': req_line.product_qty,
                        'price_unit': price_unit,
                        'taxes_id': [(6, 0, taxes_ids)],
                        'date_planned': requisition.schedule_date or fields.Date.today(),
                        'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                        'account_analytic_id': req_line.account_analytic_id.id,

                        })
                    quotation_lines.append(xval)

                    purchase_vals = {
                        'payment_term' : partner.property_supplier_payment_term_id,
                        'currency' : partner.property_purchase_currency_id or requisition.company_id.currency_id,
                        'partner_id' : partner.id,
                        'fiscal_position_id' : fpos.id,
                        'payment_term_id' : payment_term.id,
                        'company_id' : requisition.company_id.id,
                        'currency_id' : currency.id,
                        'origin' : requisition.name,
                        'partner_ref' : requisition.name,
                        'notes' : requisition.description,
                        'date_order' : requisition.date_end or fields.Datetime.now(),
                        'picking_type_id' : requisition.picking_type_id.id,
                        'order_line':quotation_lines,
                        'requisition_id': requisition.id,
                    }
                    purchase_id = purchase_obj.create(purchase_vals)
                    purchase_list.append(purchase_id.id)
                return {
                    'domain': [('id', 'in', purchase_list)],
                    'name': _('Presupuestos para %s' % requisition.name),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window'
                    }
            else:

                ####### No Fincados ########

                requisition_line_records = requisition_line.search([('requisition_id','=',requisition.id),('supplier_id','=',False),('fincamiento','=',False),('authorized','=',False)])
                quotation_lines = []
                for req_line in requisition_line_records:
                    partner = self.supplier_id

                    currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

                    payment_term = partner.property_supplier_payment_term_id

                    product_lang = req_line.product_id.with_context({
                        'lang': partner.lang,
                        'partner_id': partner.id,
                    })
                    name = product_lang.display_name
                    if product_lang.description_purchase:
                        name += '\n' + product_lang.description_purchase

                    # Compute quantity and price_unit
                    if requisition.type_id.quantity_copy != 'copy':
                        product_qty = 0
                        price_unit = req_line.price_unit
                    elif req_line.product_uom_id != req_line.product_id.uom_po_id:
                        product_qty = req_line.product_uom_id._compute_quantity(req_line.product_qty, req_line.product_id.uom_po_id)
                        price_unit = req_line.product_uom_id._compute_price(req_line.price_unit, req_line.product_id.uom_po_id)
                    else:
                        product_qty = req_line.product_qty
                        price_unit = req_line.price_unit

                    # Compute price_unit in appropriate currency
                    if requisition.company_id.currency_id != currency:
                        price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

                    FiscalPosition = self.env['account.fiscal.position']
                    fpos = FiscalPosition.get_fiscal_position(partner.id)
                    fpos = FiscalPosition.browse(fpos)

                    # Compute taxes
                    if fpos:
                        taxes_ids = fpos.map_tax(req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
                    else:
                        taxes_ids = req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

                    xval = (0,0,{
                        'name': name,
                        'product_id': req_line.product_id.id,
                        'product_uom': req_line.product_uom_id.id,
                        'product_qty': req_line.product_qty,
                        'price_unit': price_unit,
                        'taxes_id': [(6, 0, taxes_ids)],
                        'date_planned': requisition.schedule_date or fields.Date.today(),
                        'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                        'account_analytic_id': req_line.account_analytic_id.id,

                        })
                    quotation_lines.append(xval)

                    purchase_vals = {
                        'payment_term' : partner.property_supplier_payment_term_id,
                        'currency' : partner.property_purchase_currency_id or requisition.company_id.currency_id,
                        'partner_id' : partner.id,
                        'fiscal_position_id' : fpos.id,
                        'payment_term_id' : payment_term.id,
                        'company_id' : requisition.company_id.id,
                        'currency_id' : currency.id,
                        'origin' : requisition.name,
                        'partner_ref' : requisition.name,
                        'notes' : requisition.description,
                        'date_order' : requisition.date_end or fields.Datetime.now(),
                        'picking_type_id' : requisition.picking_type_id.id,
                        'order_line':quotation_lines,
                        'requisition_id': requisition.id,
                    }
                    purchase_id = purchase_obj.create(purchase_vals)
                    purchase_list.append(purchase_id.id)

                ########## Fincados ###########

                self.env.cr.execute("""
                    select supplier_id from purchase_requisition_line
                        where requisition_id = %s and fincamiento=True
                        group by supplier_id;
                    """,(requisition.id,))
                cr_res = self.env.cr.fetchall()
                supplier_list = [x[0] for x in cr_res]
                if supplier_list:
                    for supplier in supplier_list:
                        requisition_line_records = requisition_line.search([('requisition_id','=',requisition.id),('supplier_id','=',supplier),('fincamiento','=',True)])
                        quotation_lines = []
                        for req_line in requisition_line_records:
                            partner = self.env['res.partner'].browse(supplier)

                            currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

                            payment_term = partner.property_supplier_payment_term_id

                            product_lang = req_line.product_id.with_context({
                                'lang': partner.lang,
                                'partner_id': partner.id,
                            })
                            name = product_lang.display_name
                            if product_lang.description_purchase:
                                name += '\n' + product_lang.description_purchase

                            # Compute quantity and price_unit
                            if requisition.type_id.quantity_copy != 'copy':
                                product_qty = 0
                                price_unit = req_line.price_unit
                            elif req_line.product_uom_id != req_line.product_id.uom_po_id:
                                product_qty = req_line.product_uom_id._compute_quantity(req_line.product_qty, req_line.product_id.uom_po_id)
                                price_unit = req_line.product_uom_id._compute_price(req_line.price_unit, req_line.product_id.uom_po_id)
                            else:
                                product_qty = req_line.product_qty
                                price_unit = req_line.price_unit

                            # Compute price_unit in appropriate currency
                            if requisition.company_id.currency_id != currency:
                                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

                            FiscalPosition = self.env['account.fiscal.position']
                            fpos = FiscalPosition.get_fiscal_position(partner.id)
                            fpos = FiscalPosition.browse(fpos)

                            # Compute taxes
                            if fpos:
                                taxes_ids = fpos.map_tax(req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
                            else:
                                taxes_ids = req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

                            xval = (0,0,{
                                'name': name,
                                'product_id': req_line.product_id.id,
                                'product_uom': req_line.product_uom_id.id,
                                'product_qty': req_line.product_qty,
                                'price_unit': price_unit,
                                'taxes_id': [(6, 0, taxes_ids)],
                                'date_planned': requisition.schedule_date or fields.Date.today(),
                                'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                                'account_analytic_id': req_line.account_analytic_id.id,

                                })
                            quotation_lines.append(xval)

                            purchase_vals = {
                                'payment_term' : partner.property_supplier_payment_term_id,
                                'currency' : partner.property_purchase_currency_id or requisition.company_id.currency_id,
                                'partner_id' : partner.id,
                                'fiscal_position_id' : fpos.id,
                                'payment_term_id' : payment_term.id,
                                'company_id' : requisition.company_id.id,
                                'currency_id' : currency.id,
                                'origin' : requisition.name,
                                'partner_ref' : requisition.name,
                                'notes' : requisition.description,
                                'date_order' : requisition.date_end or fields.Datetime.now(),
                                'picking_type_id' : requisition.picking_type_id.id,
                                'order_line':quotation_lines,
                                'fincamiento': True,
                                'fincamiento_reference': partner.fincamiento_reference.id,
                                'requisition_id': requisition.id,
                            }
                            ### Buscando un Pedido repetido
                            purchase_prev_id = purchase_obj.search([('partner_id','=',supplier),('requisition_id','=',requisition.id),('fincamiento_reference','=',partner.fincamiento_reference.id),('state','in',('to approve','purchase'))])
                            if purchase_prev_id:
                                raise UserError(_("Error!\nYa se tiene un Pedido Fincado para el Proveedor %s" % partner.name))
                            
                            purchase_id = purchase_obj.create(purchase_vals)
                            purchase_id.sudo().button_confirm()
                            purchase_id.sudo().button_approve()
                            purchase_list.append(purchase_id.id)

                #### Autorizados ####
                self.env.cr.execute("""
                    select authorized_supplier_id from purchase_requisition_line
                        where requisition_id = %s and authorized=True
                        group by authorized_supplier_id;
                    """,(requisition.id,))
                cr_res = self.env.cr.fetchall()
                supplier_list = [x[0] for x in cr_res]
                if supplier_list:
                    for supplier in supplier_list:
                        requisition_line_records = requisition_line.search([('requisition_id','=',requisition.id),('authorized_supplier_id','=',supplier),('authorized','=',True)])
                        quotation_lines = []
                        for req_line in requisition_line_records:
                            partner = self.env['res.partner'].browse(supplier)

                            currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

                            payment_term = partner.property_supplier_payment_term_id

                            product_lang = req_line.product_id.with_context({
                                'lang': partner.lang,
                                'partner_id': partner.id,
                            })
                            name = product_lang.display_name
                            if product_lang.description_purchase:
                                name += '\n' + product_lang.description_purchase

                            # Compute quantity and price_unit
                            if requisition.type_id.quantity_copy != 'copy':
                                product_qty = 0
                                price_unit = req_line.price_unit
                            elif req_line.product_uom_id != req_line.product_id.uom_po_id:
                                product_qty = req_line.product_uom_id._compute_quantity(req_line.product_qty, req_line.product_id.uom_po_id)
                                price_unit = req_line.product_uom_id._compute_price(req_line.price_unit, req_line.product_id.uom_po_id)
                            else:
                                product_qty = req_line.product_qty
                                price_unit = req_line.price_unit

                            # Compute price_unit in appropriate currency
                            if requisition.company_id.currency_id != currency:
                                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

                            FiscalPosition = self.env['account.fiscal.position']
                            fpos = FiscalPosition.get_fiscal_position(partner.id)
                            fpos = FiscalPosition.browse(fpos)

                            # Compute taxes
                            if fpos:
                                taxes_ids = fpos.map_tax(req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
                            else:
                                taxes_ids = req_line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

                            xval = (0,0,{
                                'name': name,
                                'product_id': req_line.product_id.id,
                                'product_uom': req_line.product_uom_id.id,
                                'product_qty': req_line.product_qty,
                                'price_unit': price_unit,
                                'taxes_id': [(6, 0, taxes_ids)],
                                'date_planned': requisition.schedule_date or fields.Date.today(),
                                'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                                'account_analytic_id': req_line.account_analytic_id.id,

                                })
                            quotation_lines.append(xval)

                            purchase_vals = {
                                'payment_term' : partner.property_supplier_payment_term_id,
                                'currency' : partner.property_purchase_currency_id or requisition.company_id.currency_id,
                                'partner_id' : partner.id,
                                'fiscal_position_id' : fpos.id,
                                'payment_term_id' : payment_term.id,
                                'company_id' : requisition.company_id.id,
                                'currency_id' : currency.id,
                                'origin' : requisition.name,
                                'partner_ref' : requisition.name,
                                'notes' : requisition.description,
                                'date_order' : requisition.date_end or fields.Datetime.now(),
                                'picking_type_id' : requisition.picking_type_id.id,
                                'order_line':quotation_lines,
                                'fincamiento': False,
                                'fincamiento_reference': False,
                                'authorized': True,
                                'requisition_id': requisition.id,
                            }
                            ### Buscando un Pedido repetido
                            purchase_prev_id = purchase_obj.search([('partner_id','=',supplier),('requisition_id','=',requisition.id),('state','not in',('done','cancel'))])
                            if purchase_prev_id:
                                raise UserError(_("Error!\nYa se tiene un Pedido Autorizado para el Proveedor %s" % partner.name))
                            
                            purchase_id = purchase_obj.create(purchase_vals)
                            # purchase_id.sudo().button_confirm()
                            # purchase_id.sudo().button_approve()
                            purchase_list.append(purchase_id.id)

                return {
                    'domain': [('id', 'in', purchase_list)],
                    'name': _('Presupuestos de  %s' % requisition.name),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window'
                    }


        return True
