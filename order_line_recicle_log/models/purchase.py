# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo import tools
import pytz

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    from_done = fields.Boolean(compute='_compute_from_done', readonly=False)
    price_need_reason = fields.Boolean(compute='_compute_need_reason', readonly=False)
    reason_price_chg = fields.Char(string='Change reason', compute='_compute_reason_p_change', readonly=False)
    log_ids = fields.One2many('purchase.order.log', 'purchase_order_id')
    
    @api.one
    def _compute_from_done(self):
        fld='state'
        # VSGTN: ¿En cancelado se puede editar las líneas?
        if not self.from_done and self[fld] == 'draft':
            msgs_rs=self.message_ids.filtered(lambda r: r.tracking_value_ids.filtered(lambda s: s.field==fld))
            if msgs_rs:
                msgs_rs=msgs_rs[0].tracking_value_ids.filtered(lambda t: t.field==fld)
            else:
                return
            idx_cancel=[y[0] for y in self._fields[fld].selection].index('cancel')
            idx_draft=[y[0] for y in self._fields[fld].selection].index('draft')
            tr_rs=self.env['ir.translation']
            str_ant = tr_rs.search([('type', '=', 'selection'),('name','=',self._name+','+fld),('source','=',self._fields[fld].selection[idx_cancel][1])]).value
            str_nvo = tr_rs.search([('type', '=', 'selection'),('name','=',self._name+','+fld),('source','=',self._fields[fld].selection[idx_draft][1])]).value
            
            if msgs_rs.old_value_char == str_ant and msgs_rs.new_value_char == str_nvo:
                self.from_done = True
        
    @api.one
    def _compute_need_reason(self):
        if not self.price_need_reason:
            self.price_need_reason = False
            
    @api.one
    def _compute_reason_p_change(self):
        if not self.reason_price_chg:
            self.reason_price_chg = ''
    
    @api.onchange('order_line')
    def onchg_order_line(self):
        if self.from_done:
            idx=0
            for line in self.order_line:
                if line.price_unit != self._origin.order_line[idx].price_unit:
                    self.price_need_reason = True
                    return
                idx+=1
    
    @api.multi
    def write(self, vals):
        if 'price_need_reason' in vals:
            origs = {}
            reason = vals.pop('reason_price_chg')
            order_lines=vals['order_line']
            for line in order_lines:
                if not line[2]:
                    continue
                origs[line[1]]=self.order_line.filtered(lambda r: r.id == line[1]).price_unit
            vals.pop('price_need_reason')
        res = super(PurchaseOrder, self).write(vals)
        if 'reason' in vars():
            utz=pytz.timezone(self.env.context['tz'])
            subtype_xmlid = 'order_line_recicle_log.mt_po_price_log'
            subtype_rec = self.env.ref(subtype_xmlid)
            date=tools.datetime.now(utz)
            detail = ""
            log_rec = self.env['purchase.order.log']
            for line in order_lines:
                if not line[2]:
                    continue
                line_id = self.order_line.filtered(lambda r: r.id == line[1])
                detail += "<b><a href=# data-oe-model=product.product data-oe-id=%d>%s</a></b>: %s<br />" % (line_id.product_id, line_id.name, line[2]['price_unit'])
                log_rec.create({'purchase_order_id': self.id, 'date': date.astimezone(pytz.UTC), 'user_id': self.env.user.id, 
                    'product_id': line_id.product_id.id, 'old_value': origs[line[1]], 'new_value': line[2]['price_unit'], 'reason': reason})
            message = _(
                'The user <a href=# data-oe-model=res.users data-oe-id=%d>%s</a> on %s made this modification:<br /><br />%s</br><b>Reason:</b> %s'
            )
            self.message_post(
                body=message % (self.env.user.id, self.env.user.name, 
                                date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT), detail, reason), 
                subject=subtype_rec.description, 
                subtype=subtype_xmlid
            )
        return res
    
class SupplierInfoLog(models.Model):
    _name = 'purchase.order.log'
    
    purchase_order_id = fields.Many2one('purchase.order')
    date = fields.Datetime(string="Date")
    user_id = fields.Many2one('res.users', string="User")
    product_id = fields.Many2one('product.product')
    old_value = fields.Char(string="Old Value")
    new_value = fields.Char(string="New Value")
    reason = fields.Char(string="Reason")
