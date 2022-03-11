# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class SaleOrderLineDiff(models.Model):
    _name = 'explode.lvl.bom.config.lines'
    _order = 'qty_level'
    _auto = False
    
    product_id = fields.Many2one('product.product', string='Product')
    stock_offset = fields.Float('Stock Offset')
    qty_available = fields.Float('Available Quantity')
    qty_level = fields.Float('Quantity to Level')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'explode_lvl_bom_config_lines')
        stock_location = self.env['stock.location'].browse(
            self.env['ir.values'].get_default('purchase.config.settings', 'stock_product')
        )
        sql="""DROP VIEW IF EXISTS product_apt_stock;
            CREATE VIEW product_apt_stock AS (
             SELECT 
              sq.product_id,
              sum(sq.qty) as qty_available
             FROM "stock_location" as sl, stock_quant as sq 
             LEFT JOIN "product_product" as pp ON (sq."product_id" = pp."id") 
             LEFT JOIN "product_template" as pt ON (pp."product_tmpl_id" = pt."id")
             WHERE (sq."location_id"=sl."id") AND sl."parent_left" >= %s AND  sl."parent_left" < %s
             GROUP BY sq."product_id", pp."default_code", pp."id"
             ORDER BY pp."default_code", pp."id"
            );
            
            DROP VIEW IF EXISTS product_moves_stats_90;
            CREATE VIEW product_moves_stats_90 AS (
             select 
              pt.id as product_tmpl_id, 
              pp.id as product_id, 
              sum(CASE WHEN sm.location_id IN (select sl.id from stock_location sl where sl.usage = 'internal' and sl.active=True) THEN sm.product_qty ELSE 0 END) as sum_qty, 
              sum(CASE WHEN sm.location_id IN (select sl.id from stock_location sl where sl.usage = 'customer' and sl.active=True) THEN sm.product_qty ELSE 0 END) as desc_qty 
             from stock_move sm
              inner join product_product pp on sm.product_id=pp.id 
              inner join product_template pt on pp.product_tmpl_id=pt.id 
             where sm.state='done' and 
              sm.date::timestamp::date >= (select (select current_date at time zone 'UTC-6') - interval '90 days')::timestamp::date and 
              sm.date::timestamp::date <= (select current_date at time zone 'UTC-6')::timestamp::date and
              pt.sale_ok=True and 
              (
               (
               sm.location_dest_id IN (select sl.id from stock_location sl where sl.usage = 'customer' and sl.active=True) and 
               sm.location_id IN (select sl.id from stock_location sl where sl.usage = 'internal' and sl.active=True) 
               ) OR
               (
               sm.location_dest_id IN (select sl.id from stock_location sl where sl.usage = 'internal' and sl.active=True) and 
               sm.location_id IN (select sl.id from stock_location sl where sl.usage = 'customer' and sl.active=True) 
               )
              )
             group by pt.id, pp.id
            );

            DROP VIEW IF EXISTS explode_lvl_bom_config_lines;
            CREATE VIEW explode_lvl_bom_config_lines AS (
             SELECT 
              sqry.product_id as id,
              sqry.product_id,
              CASE WHEN (sqry.stock_offset IS NULL) THEN 0 ELSE sqry.stock_offset END AS stock_offset,
              CASE WHEN (sqry.qty_available IS NULL) THEN 0 ELSE sqry.qty_available END AS qty_available,
              CASE WHEN (sqry.qty_available IS NULL) THEN CASE WHEN sqry.stock_offset<0 THEN 0 ELSE sqry.stock_offset END ELSE CASE WHEN (sqry.stock_offset-sqry.qty_available)<0 THEN 0 ELSE sqry.stock_offset-sqry.qty_available END END as qty_level,
              CASE WHEN (pms90.sum_qty IS NULL) THEN 0 ELSE pms90.sum_qty-pms90.desc_qty END AS sum_qty
             FROM (
              SELECT 
               pp.id as product_id,
               pt.stock_offset,
               pas.qty_available,
               pt.stock_offset-pas.qty_available AS qty_level 
              FROM product_product pp 
              INNER JOIN product_template pt on pt.id=pp.product_tmpl_id
              LEFT JOIN product_apt_stock pas on pp.id=pas.product_id 
              WHERE pt.type='product' and pt.sale_ok IS TRUE AND pt.can_be_expensed IS FALSE
             ) sqry
             LEFT OUTER JOIN product_moves_stats_90 pms90 ON pms90.product_id=sqry.product_id
            )
        """ % (stock_location.parent_left, stock_location.parent_right)
        
        self._cr.execute(sql)
