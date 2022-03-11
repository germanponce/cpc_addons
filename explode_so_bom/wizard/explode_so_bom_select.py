# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import pytz

class Picking(models.TransientModel):
    _name = "explode.so.bom.select"
    days = fields.Selection([(3,'3'),(7,'7'),(14,'14'),(30,'30')],'Days to project')
    
    def process(self):
        prd_stk=self.env['ir.values'].get_default('purchase.config.settings', 'stock_product')
        if not self.env['ir.values'].get_default('purchase.config.settings', 'stock_location') or not prd_stk:
            raise UserError(_("ERROR: You must set locations for Stock comparison before use this function.") )
        utz=pytz.timezone(self.env.user.tz)
        date=tools.datetime.now(utz)
        time_delta = tools.timedelta(hours=date.hour, minutes=date.minute, seconds=date.second, microseconds=date.microsecond)
        date_ini=date-time_delta
        time_delta = tools.timedelta(days=1)
        date_ini=date_ini+time_delta
        time_delta = tools.timedelta(days=self.days)
        date_fin=date_ini+time_delta
        sql="""
            delete from explode_so_bom_config;
            insert into explode_so_bom_config
            select so.id from sale_order so where so.commitment_date2<'%s' and so.state in ('sale','done','toconfirm') and so.x_sale_order_cerrada is False;
            
            select sol.product_id as id,sol.product_id,sum(sol.product_uom_qty-sol.qty_delivered) as product_uom_qty 
            from sale_order_line sol 
            where sol.order_id in 
             (select * from explode_so_bom_config)
            and sol.qty_delivered<sol.product_uom_qty
            group by sol.product_id;
        """ % (date_fin.astimezone(pytz.UTC).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT),)
        self.env.cr.execute(sql)
        pp=self.env['product.product']
        res_qry=self.env.cr.fetchall()
        no_ids=[]
        for i,line in enumerate(res_qry):
            if line[2]<=0:
                continue
            pp=pp.browse(line[1])
            exst=pp.with_context({'location':prd_stk}).qty_available
            if exst>=line[2]:
                continue
            no_ids.append("(%d,%d,%s)"%(line[0],line[1],line[2]-exst))
        sql="""
            delete from explode_so_bom_config_lines;
            insert into explode_so_bom_config_lines values %s
        """ %','.join(no_ids)
        self.env.cr.execute(sql)
        return {
            'type': 'ir.actions.act_window',
            'name': _('%s days projection (%s - %s)')%(
                self.days,date_ini.strftime('%Y/%m/%d %H:%M'),date_fin.strftime('%Y/%m/%d %H:%M')
            ),
            'res_model': 'explode.so.bom',
            'view_mode': 'tree',
            'view_type': 'form',
            'views': [(False, 'tree')],
            'target': 'main',
            #'context': {'search_default_groupby_categ_id': True},
        }
