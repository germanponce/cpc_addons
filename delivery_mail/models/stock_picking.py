# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = "stock.picking"
    
    @api.one
    def _get_partial(self):
        self.partial_msg = "" if 2>len(self.sale_id.picking_ids) else _(" partially")
        
    def _get_products_html(self):
        for rec in self:
            res="<table cellspacing='0' cellpadding='0' border='0' style='width: 600px; margin-top: 5px;'><thead><tr><th>%s</th><th>%s</th></tr></thead><tbody>"
            res=res%(_('Product'),_('Quantity'))
            for itm in rec.pack_operation_product_ids:
                res+=("    <tr><td>%s</td><td>%s</td></tr>\n"%(itm.product_id.name,itm.qty_done))
            res+='</tbody></table>'
            rec.products_table=res
    
    partial_msg = fields.Char(compute='_get_partial')
    products_table = fields.Char(compute='_get_products_html')
    
    @api.multi
    def do_transfer(self):
        res = super(Picking, self).do_transfer()
        #Sólo se enviará cuando es operación de salida
        if self.picking_type_id.code == 'outgoing' and self.sale_id:
            emails = self.env['mail.mail']
            tplt_cstm=self.env['mail.template'].browse(self.env['ir.values'].get_default('delivery.mail.settings', 'customer_template'))
            email_msg_cstm=tplt_cstm.generate_email(self.id, fields=['body_html', 'subject'])
            email_msg_cstm['recipient_ids']=[(4, self.sale_id.partner_id.id)]
            email=self.env['mail.mail'].create(email_msg_cstm)
            emails|=email
            tplt_agnt=self.env['mail.template'].browse(self.env['ir.values'].get_default('delivery.mail.settings', 'agent_template'))
            email_msg_agnt=tplt_agnt.generate_email(self.id, fields=['body_html', 'subject'])
            email_msg_agnt['recipient_ids']=[(4, self.sale_id.user_id.partner_id.id)]
            email=self.env['mail.mail'].create(email_msg_agnt)
            emails|=email
            emails.send()
        return res
