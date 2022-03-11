# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import tools
import pytz

class SupplierInfo(models.Model):
    _name = 'product.supplierinfo'
    _inherit = ['product.supplierinfo', 'ir.needaction_mixin', 'mail.thread']
    
    price_need_reason = fields.Boolean(compute='_compute_need_reason', readonly=False)
    reason_price_chg = fields.Char(string='Change reason', compute='_compute_reason_p_change', readonly=False)
    log_ids = fields.One2many('product.supplierinfo.log', 'supplierinfo_id')
    
    @api.onchange('name', 'price', 'min_qty', 'product_tmpl_id', 'product_id', 'currency_id', 'date_start', 'date_end')
    def onchg_fields_pl(self):
        fields=self._origin._onchange_methods.keys()
        for field in fields:
            if self[field] != self._origin[field]:
                self.price_need_reason = True
                return
        self.price_need_reason = False
    
    @api.one
    def _compute_need_reason(self):
        if not self.price_need_reason:
            self.price_need_reason = False
    
    @api.one
    def _compute_reason_p_change(self):
        if not self.reason_price_chg:
            self.reason_price_chg = ''
        
    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, vals):
        res = super(SupplierInfo, self).create(vals)
        if 'price' in vals:
            utz=pytz.timezone(self.env.context['tz'])
            reason = _('Supplier Information Created')
            price_orig = 0.0
            subtype_xmlid = 'product_supplierinfo_log.mt_price_log'
            subtype_rec = self.env.ref(subtype_xmlid)
            message = _(
                'Supplier information created by <a href=# data-oe-model=res.users data-oe-id=%d>%s</a> on %s :<br /><b>Supplier:</b> %s<br /><b>Product:</b> %s<br /><b>Price:</b> %s'
            )
            date=tools.datetime.now(utz)
            res.message_post(
                body=message % (res.env.user.id, res.env.user.name, 
                                date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT), 
                                res.name.name, 
                                res.product_tmpl_id.name, 
                                res.price), 
                subject=subtype_rec.description, 
                subtype=subtype_xmlid
            )
            log_rec = self.env['product.supplierinfo.log']
            log_rec.create({'supplierinfo_id': res.id, 'date': date.astimezone(pytz.UTC), 'user_id': res.env.user.id, 
                            'field': _('Price'), 'old_value': price_orig, 
                            'new_value': res.price, 'reason': reason})
        return res
    
    @api.multi
    def write(self, vals):
        if 'reason_price_chg' in vals:
            origs = {}
            reason = vals.pop('reason_price_chg')
            vals.pop('price_need_reason')
            for val in vals:
                origs[val]=self[val]
        res = super(SupplierInfo, self).write(vals)
        if 'reason' in vars():
            utz=pytz.timezone(self.env.context['tz'])
            subtype_xmlid = 'product_supplierinfo_log.mt_price_log'
            subtype_rec = self.env.ref(subtype_xmlid)
            date=tools.datetime.now(utz)
            fields=self._onchange_methods
            detail = ""
            log_rec = self.env['product.supplierinfo.log']
            for val in vals:
                if val in fields:
                    new_value = self[val].name if isinstance(self[val], models.Model) else self[val]
                    field = _(self._fields[val].string)
                    detail += "<b>%s</b>: %s<br />" % (field, new_value)
                    log_rec.create({'supplierinfo_id': self.id, 'date': date.astimezone(pytz.UTC), 'user_id': self.env.user.id, 
                        'field': field, 
                        'old_value': origs[val].name if isinstance(origs[val], models.Model) else origs[val], 
                        'new_value': new_value, 'reason': reason})
            message = _(
                'The user <a href=# data-oe-model=res.users data-oe-id=%d>%s</a> on %s made this modification:<br />%s</br><b>Reason:</b> %s'
            )
            self.message_post(
                body=message % (self.env.user.id, self.env.user.name, 
                                date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT), detail, reason), 
                subject=subtype_rec.description, 
                subtype=subtype_xmlid
            )
        return res
    
class SupplierInfoLog(models.Model):
    _name = 'product.supplierinfo.log'
    
    supplierinfo_id = fields.Many2one('product.supplierinfo')
    date = fields.Datetime(string="Date")
    user_id = fields.Many2one('res.users', string="User")
    field = fields.Char(string="Field")
    old_value = fields.Char(string="Old Value")
    new_value = fields.Char(string="New Value")
    reason = fields.Char(string="Reason")
