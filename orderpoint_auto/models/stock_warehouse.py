# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import pytz

class Orderpoint(models.Model):
    _name =  'stock.warehouse.orderpoint'
    _inherit = ["stock.warehouse.orderpoint", 'ir.needaction_mixin', 'mail.thread']

    def automatic_orderpoint(self):
        utz = pytz.timezone('America/Mexico_City')
        date = tools.datetime.now(utz)
        time_delta = tools.timedelta(hours=date.hour, minutes=date.minute, seconds=date.second, microseconds=date.microsecond)
        date_fin = date-time_delta
        time_delta = tools.timedelta(days=90)
        date_ini = date_fin-time_delta

        sql = """select smls.product_tmpl_id, smls.product_id, smls.prom_qty,array_agg(ps.id) as supplier_info_ids, array_agg(ps.delay) as delays, array_agg(ps.min_qty) min_qtys,array_agg(ps.delay*smls.prom_qty*2) as res_mins, array_agg(CASE WHEN ps.delay*smls.prom_qty>ps.min_qty THEN ps.delay*smls.prom_qty*2 ELSE ps.delay*smls.prom_qty+ps.min_qty END) as res_maxs
        from (
         select pt.id as product_tmpl_id, pp.id as product_id, sum(sm.product_qty)/90 as prom_qty 
         from stock_move sm
         inner join product_product pp on sm.product_id=pp.id 
         inner join product_template pt on pp.product_tmpl_id=pt.id 
         where sm.state='done' and 
         sm.date > '%s' and
         sm.date < '%s' and 
         pt.purchase_ok=True and 
         sm.location_dest_id in (select sl.id from stock_location sl where sl.usage in ('production','inventory'))
         group by pt.id, pp.id 
         ) smls
        inner join product_supplierinfo ps on ps.product_tmpl_id=smls.product_tmpl_id
        group by smls.product_tmpl_id,smls.product_id,smls.prom_qty
        """ % (
            date_ini.astimezone(pytz.UTC).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT), 
            date_fin.astimezone(pytz.UTC).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        )
        self.env.cr.execute(sql)
        res=self.env.cr.fetchall()
        
        sw=self.env['stock.warehouse'].browse(2)
        
        for itm in res:
            pp=self.env['product.product'].browse(itm[1])
            if len(pp.orderpoint_ids)>0:
                op=pp.orderpoint_ids[0]
                op.write({'product_min_qty':itm[6][0],'product_max_qty':itm[7][0]})
            else:
                op=self.create({
                    'product_id': pp.id,
                    'location_id': sw.lot_stock_id.id,
                    'warehouse_id': sw.id,
                    'product_min_qty':itm[6][0], 
                    'product_max_qty':itm[7][0], 
                })
            psi=self.env['product.supplierinfo'].browse(itm[3][0])
            msg=_(
                '<p>Orderpoint automatically created, it is based on this data:<p/><p><strong>Initial date for statistics:</strong>%s<br /><strong>Average consumption:</strong>%s<br /><strong>Supplier:</strong>%s<br /><strong>Delay:</strong>%s<br /><strong>Minimal Supplier Quantity:</strong>%s</p>'
            )
            op.message_post(
                body=msg % (date_ini.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT), itm[2], psi.name.name, psi.delay, psi.min_qty),
                subject='Orderpoint for %s on %s' % (pp.name, date_fin.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                subtype='mail.mt_note',
            )
        
