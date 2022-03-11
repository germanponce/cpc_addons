# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _

class OrderpointReport(models.Model):
    _name =  'stock.warehouse.orderpoint.report'
    _order = 'categ_id'
    _auto = False

    product_id = fields.Many2one('product.product', string="Product")
    categ_id = fields.Many2one('purchase.category', sting="Category")
    uom_id = fields.Many2one('product.uom', string='UoM')
    package_type = fields.Char('Package Type')
    sum_qty = fields.Float('Total consumption')
    prom_qty = fields.Float('Daily Average Consumption')
    supplier_info_id = fields.Many2one('product.supplierinfo', string="Supplier Information")
    delay = fields.Integer('Delay')
    delay_x_cpd = fields.Float('Delay X DAC')
    min_qty = fields.Float('Min. Qty')
    res_max = fields.Float('Maximum')
    res_min = fields.Float('Minimum')
    qty_req = fields.Float('Required')
    qty_available = fields.Float('Available Quantity',compute='_comp_qty')
    qty_virtual = fields.Float('Virtual Quantity',compute='_comp_qty')
    qty_in = fields.Float('Incoming Quantity',compute='_comp_qty')
    qty_out = fields.Float('Outgoing Quantity',compute='_comp_qty')
    qty_sugg = fields.Float('Purchase Sugg. Qty',compute='_comp_qty')

    @api.one
    def _comp_qty(self):
        stock_location = self.env['ir.values'].get_default('purchase.config.settings', 'stock_location')
        self.qty_available = self.product_id.with_context({'location':stock_location}).qty_available
        self.qty_virtual = self.product_id.with_context({'location':stock_location}).virtual_available
        self.qty_in = self.product_id.with_context({'location':stock_location}).incoming_qty
        self.qty_out = self.product_id.with_context({'location':stock_location}).outgoing_qty
        self.qty_sugg = (self.res_max+self.qty_req)-(self.qty_available+self.qty_in)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'stock_warehouse_orderpoint_report')
        sql="""DROP VIEW IF EXISTS stock_warehouse_orderpoint_report ;
        DROP VIEW IF EXISTS explode_lvl_bom;
        drop FUNCTION IF EXISTS explode_lvl();
        CREATE OR REPLACE FUNCTION explode_lvl() 
        RETURNS TABLE (
        id INT,
        product_id INT,
        categ_id INT,
        uom_id INT,
        qty FLOAT,
        sum_qty NUMERIC
        )
        as $$
            BEGIN
            DROP TABLE IF EXISTS no_bom_prods;
            CREATE TEMP TABLE no_bom_prods AS
            SELECT pp.id AS id, pp.id AS product_id, pt.categ_id, pt.uom_id, pqsol.qty_level AS product_qty, pqsol.sum_qty
            FROM explode_lvl_bom_config_lines AS pqsol
            INNER JOIN product_product pp ON pp.id=pqsol.product_id
            INNER JOIN product_template pt ON pp.product_tmpl_id=pt.id
            WHERE pqsol.id NOT IN (SELECT imb.product_id FROM mrp_bom imb WHERE imb.product_id IS NOT NULL);
            
            drop table if exists bom_lvl_all;
            create temp table bom_lvl_all as 
            select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.qty_level) as product_qty, SUM(mbl.product_qty*pqsol.sum_qty) AS sum_qty
            from explode_lvl_bom_config_lines as pqsol
            inner join mrp_bom mb on mb.product_id=pqsol.product_id 
            inner join mrp_bom_line mbl on mbl.bom_id=mb.id
            inner join product_product pp on pp.id=mbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            group by mbl.product_id,pt.categ_id,pt.uom_id;
            
            drop table if exists prd_lvl_ept;
            create temp table prd_lvl_ept as 
            select pp.id,pp.id as product_id,pt.categ_id,pt.uom_id,sum(pmbl.product_qty) as product_qty, SUM(pmbl.sum_qty) AS sum_qty
            from bom_lvl_all as pmbl
            inner join product_product pp on pp.id=pmbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            where pt.purchase_ok is False and pt.sale_ok is False and pt.can_be_expensed is False
            group by pp.id,pt.categ_id,pt.uom_id;
            
            drop table if exists bom_lvl_int;
            create temp table bom_lvl_int as 
            select * from bom_lvl_all 
            except 
            select * from prd_lvl_ept;
            
            drop table if exists bom_lvl_all;
            create temp table bom_lvl_all as 
            select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.product_qty) as product_qty, SUM(mbl.product_qty*pqsol.sum_qty) AS sum_qty 
            from prd_lvl_ept as pqsol
            inner join mrp_bom mb on mb.product_id=pqsol.product_id 
            inner join mrp_bom_line mbl on mbl.bom_id=mb.id
            inner join product_product pp on pp.id=mbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            group by mbl.product_id,pt.categ_id,pt.uom_id;
            
            drop table if exists prd_lvl_ept;
            create temp table prd_lvl_ept as 
            select pp.id,pp.id as product_id,pt.categ_id,pt.uom_id,sum(pmbl.product_qty) as product_qty, SUM(pmbl.sum_qty) AS sum_qty 
            from bom_lvl_all as pmbl
            inner join product_product pp on pp.id=pmbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            where pt.purchase_ok is False and pt.sale_ok is False and pt.can_be_expensed is False
            group by pp.id,pt.categ_id,pt.uom_id;
            
            drop table if exists bom_lvl_fnl;
            create temp table bom_lvl_fnl as 
            select * from bom_lvl_all 
            except 
            select * from prd_lvl_ept;
            
            return query select 
             sqry.id, 
             sqry.product_id, 
             sqry.categ_id, 
             sqry.uom_id,
             sum(sqry.product_qty) as product_qty,
             sum(sqry.sum_qty) as sum_qty
            from 
             (
              select * from no_bom_prods 
              union 
              select * from bom_lvl_fnl 
              union 
              select * from bom_lvl_int 
              union 
              select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.product_qty) as product_qty, SUM(mbl.product_qty*pqsol.sum_qty) AS sum_qty
              from prd_lvl_ept as pqsol
              inner join mrp_bom mb on mb.product_id=pqsol.product_id 
              inner join mrp_bom_line mbl on mbl.bom_id=mb.id
              inner join product_product pp on pp.id=mbl.product_id
              inner join product_template pt on pp.product_tmpl_id=pt.id
              group by mbl.product_id,pt.categ_id,pt.uom_id
             ) sqry
            group by sqry.id, sqry.product_id, sqry.categ_id, sqry.uom_id;
        END $$ 
        LANGUAGE 'plpgsql';
        
        CREATE OR REPLACE FUNCTION materials_to_product_lvl(id_arg INTEGER)
        RETURNS TABLE (
         id INT
        )
        AS $$
         DECLARE
         iterar INTEGER :=1;
         producir BOOLEAN := TRUE;
         -- msg TEXT;
         BEGIN

         DROP TABLE IF EXISTS ept_pnd;
         CREATE TEMP TABLE ept_pnd(product_id INT);
         INSERT INTO ept_pnd VALUES (id_arg);

         DROP TABLE IF EXISTS purchase_fnl;
         CREATE TEMP TABLE purchase_fnl(product_id INT);
         
         IF EXISTS (SELECT 1 FROM mrp_bom WHERE product_id=id_arg) THEN
            SELECT TRUE INTO producir;
         ELSEIF EXISTS (SELECT 1 FROM mrp_bom_line WHERE product_id=id_arg) THEN
            SELECT TRUE INTO producir;
         ELSE
            SELECT FALSE INTO producir;
            SELECT 0 INTO iterar;
            INSERT INTO purchase_fnl VALUES (id_arg);
         END IF;

         WHILE iterar>0 LOOP
          -- select array_agg(product_id) into msg from ept_pnd;
          -- RAISE NOTICE 'Inicio con %',msg;
          DROP table IF EXISTS purchase_all;
          CREATE TEMP TABLE purchase_all AS
          SELECT mb.product_id 
          FROM mrp_bom_line mbl 
          INNER JOIN mrp_bom mb ON mb.id=mbl.bom_id 
          WHERE mbl.product_id in (select ept_pnd.product_id from ept_pnd)
          group by mbl.product_id,mbl.bom_id,mb.product_id;
          -- select array_agg(product_id) into msg from purchase_all;
          -- RAISE NOTICE 'Existo con %',msg;

          DROP table IF EXISTS ept_pnd;
          create temp table ept_pnd as
          select pa.product_id 
          from purchase_all pa 
          inner join product_product pp on pp.id=pa.product_id
          inner join product_template pt on pp.product_tmpl_id=pt.id
          where pt.purchase_ok is False and pt.sale_ok is False and pt.can_be_expensed is False;
          -- select array_agg(product_id) into msg from ept_pnd;
          -- RAISE NOTICE 'Debo excluir a %',msg;

          insert into purchase_fnl 
          select pa.product_id from purchase_all pa
          except 
          select ept_pnd.product_id from ept_pnd;
          
          SELECT count(ept_pnd.product_id) INTO iterar FROM ept_pnd;
          -- RAISE NOTICE 'Aún debo iterar % veces', iterar;
         END LOOP;
         return query 
         select purchase_fnl.product_id 
         from purchase_fnl 
         where purchase_fnl.product_id in (select bcl.product_id from explode_lvl_bom_config_lines bcl)
         group by purchase_fnl.product_id;
        END $$
        LANGUAGE 'plpgsql';
        
        DROP VIEW IF EXISTS explode_lvl_bom;
        CREATE VIEW explode_lvl_bom AS (
         SELECT 
          pt.id as product_tmpl_id,
          elvl.product_id,
          elvl.categ_id,
          pt.purchase_clasif,
          elvl.uom_id,
          pt.package_type,
          elvl.qty as qty_req,
          elvl.sum_qty as sum_qty,
          elvl.sum_qty/90 as prom_qty
         FROM explode_lvl() elvl 
         INNER JOIN product_product pp on elvl.product_id=pp.id 
         INNER JOIN product_template pt on pp.product_tmpl_id=pt.id
         GROUP BY pt.id, elvl.product_id, elvl.categ_id, pt.purchase_clasif, elvl.uom_id, pt.package_type, elvl.qty, elvl.sum_qty
        );
        
        create view stock_warehouse_orderpoint_report AS (
         select 
             qry.product_id as id,
             qry.product_id as product_id,
             qry.purchase_clasif as categ_id,
             qry.uom_id as uom_id,
             qry.package_type as package_type, 
             qry.sum_qty as sum_qty,
             qry.prom_qty as prom_qty,
             qry.supplier_info_id as supplier_info_id,
             qry.delay as delay,
             qry.delay_x_cpd as delay_x_cpd,
             qry.min_qty as min_qty,
             qry.res_max as res_max,
             qry.res_min as res_min,
             (CASE WHEN qry.qty_req IS NULL THEN 0 ELSE qry.qty_req END) as qty_req
         from (
          select 
           smls.product_tmpl_id, 
           smls.product_id, 
           smls.categ_id, 
           smls.uom_id, 
           smls.package_type, 
           smls.purchase_clasif, 
           smls.sum_qty, 
           smls.prom_qty,
           (array_agg(ps.id))[1] as supplier_info_id, 
           (array_agg(ps.delay))[1] as delay, 
           (array_agg(ps.delay*smls.prom_qty))[1] as delay_x_cpd, 
           (array_agg(ps.min_qty))[1] min_qty, 
           (array_agg(ps.delay*smls.prom_qty*2))[1] as res_min, 
           (array_agg(CASE WHEN ps.delay*smls.prom_qty>ps.min_qty THEN ps.delay*smls.prom_qty*2 ELSE ps.delay*smls.prom_qty+ps.min_qty END))[1] as res_max, 
           smls.qty_req 
          from explode_lvl_bom smls
          inner join product_supplierinfo ps on ps.product_tmpl_id=smls.product_tmpl_id
          group by smls.product_tmpl_id,smls.product_id,smls.categ_id,smls.uom_id,smls.package_type,smls.purchase_clasif,smls.sum_qty,smls.prom_qty,smls.qty_req
         ) qry
         group by qry.product_id,qry.uom_id,qry.package_type,qry.purchase_clasif,qry.sum_qty,prom_qty,qry.supplier_info_id,qry.delay,qry.delay_x_cpd,qry.min_qty,qry.res_max,qry.res_min, qry.qty_req 
        )"""
        
        self._cr.execute(sql)

    @api.multi
    def button_view_stat_moves(self):
        sql="""
        select sm.id 
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
         ) and
         sm.product_id IN (select * from materials_to_product_lvl(%s));
        """ % self.product_id.id
        self.env.cr.execute(sql)
        res_qry=self.env.cr.fetchall()
        ids_pol_proj=','.join(["%s"%j[0] for j in res_qry])
        return {
            'name': _('%s: %s')%(self.product_id.name, self.sum_qty),
            'type': 'ir.actions.act_window',
            'views': [ (self.env.ref('orderpoint_auto.view_stock_move_tree_orderpoint_rpt').id ,'tree'),],
            'target': 'current',
            'domain': "[('id','in',(%s,))]"%ids_pol_proj,
            'res_model': 'stock.move',
        }
    
    @api.multi
    def button_view_in_moves(self):
        stock_location = self.env['ir.values'].get_default('purchase.config.settings', 'stock_location')
        pp_ctx=self.env['product.product'].with_context({'location':stock_location}).browse(self.product_id.id)
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = pp_ctx._get_domain_locations()
        domain_move_in = [('product_id', 'in', pp_ctx.ids)] + domain_move_in_loc
        domain_move_in_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_in
        action = self.env.ref('stock.stock_move_action')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [ (False ,'tree'),(False,'form')],
            'target': action.target,
            'domain': domain_move_in_todo,
            'res_model': action.res_model,
        }
        
    @api.multi
    def button_view_level_detail(self):
        sql="select * from materials_to_product_lvl(%s)" % self.product_id.id
        self.env.cr.execute(sql)
        res_qry=self.env.cr.fetchall()
        ids_pol_proj=','.join(["%s"%j[0] for j in res_qry])
        return {
            'name': _('%s: %s')%(self.product_id.name, self.qty_req),
            'type': 'ir.actions.act_window',
            'views': [ (False ,'tree'),],
            'target': 'current',
            'domain': "[('id','in',(%s,))]"%ids_pol_proj,
            'res_model': 'explode.lvl.bom.config.lines',
            #'context': {'search_default_groupby_product': True, 'search_default_deliver_filter': True}
        }

