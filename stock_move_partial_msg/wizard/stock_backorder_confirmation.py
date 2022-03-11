# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    
    @api.one
    def _process(self, cancel_backorder=False):
        detail = ""
        for pack in self.pick_id.pack_operation_ids:
            detail += "<b><a href=# data-oe-model=product.product data-oe-id=%d>%s</a></b>: Requested=<b>%s</b>, Supplied=<b>%s</b><br />" % (
                pack.product_id.id, pack.product_id.name, pack.product_qty, pack.qty_done
            )
        super(StockBackorderConfirmation, self)._process(cancel_backorder)
        message="Movement <b><a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a></b> is coming partially:<br /><br />%s"
        if self.pick_id.origin:
            picking = self.pick_id.search([('name','=',self.pick_id.origin)])
        else:
            picking=self.pick_id
        # VSGTN: Considerar sudo: picking.sudo().message_post(
        picking.message_post(
            body=message % (self.pick_id.id, self.pick_id.name, detail), 
            subject=_("Partial movement notification."), message_type='email'
        )
