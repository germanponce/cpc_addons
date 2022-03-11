# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp

class SaleOrderLineDiff(models.Model):
    _name = 'sale.order.line.diff'
    _order = 'qty_to_deliver'
    _auto = False
    
    product_id = fields.Many2one('product.product', string='Product')
    qty_available = fields.Float('Available Quantity',compute='_comp_qty')
    order_id = fields.Many2one('sale.order', string='Order Reference')
    order_partner_id = fields.Many2one('res.partner', string='Customer')
    commitment_date2 = fields.Datetime(string='Raloy Date')
    name = fields.Text(string='Description')
    salesman_id = fields.Many2one('res.users', string='Salesperson')
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    qty_delivered = fields.Float(string='Delivered', digits=dp.get_precision('Product Unit of Measure'))
    qty_to_deliver = fields.Float(string='Pending', digits=dp.get_precision('Product Unit of Measure'))
    product_uom = fields.Many2one('product.uom', string='Unit of Measure')
    
    @api.one
    def _comp_qty(self):
        stock_location = self.env['ir.values'].get_default('purchase.config.settings', 'stock_product')
        self.qty_available = self.product_id.with_context({'location':stock_location}).qty_available
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'sale_order_line_diff')
        sql="""create view sale_order_line_diff AS (
         select
          sol.id,
          sol.product_id,
          sol.order_id,
          sol.order_partner_id,
          so.commitment_date2,
          sol.name,
          sol.salesman_id,
          sol.product_uom_qty,
          sol.qty_delivered,
          sol.product_uom_qty-sol.qty_delivered as qty_to_deliver,
          sol.product_uom
         from sale_order_line sol 
         inner join sale_order so on so.id=sol.order_id 
        )
        """
        self._cr.execute(sql)

class ExplodeSOBoM(models.Model):
    _name = 'explode.so.bom'
    _order = 'categ_id'
    _auto = False
    
    product_id = fields.Many2one('product.product', string='Product')
    categ_id = fields.Many2one('product.category', string='Category')
    uom_id = fields.Many2one('product.uom', string='UoM')
    qty = fields.Float('Required Quantity')
    qty_available = fields.Float('Available Quantity',compute='_comp_qty')
    qty_virtual = fields.Float('Virtual Quantity',compute='_comp_qty')
    qty_in = fields.Float('Incoming Quantity',compute='_comp_qty')
    qty_out = fields.Float('Outgoing Quantity',compute='_comp_qty')
    qty_diff = fields.Float('Difference',compute='_comp_qty')
    qty_diff_vrt = fields.Float('Difference W/Virt',compute='_comp_qty')
    
    @api.one
    def _comp_qty(self):
        stock_location = self.env['ir.values'].get_default('purchase.config.settings', 'stock_location')
        self.qty_available = self.product_id.with_context({'location':stock_location}).qty_available
        self.qty_virtual = self.product_id.with_context({'location':stock_location}).virtual_available
        self.qty_in = self.product_id.with_context({'location':stock_location}).incoming_qty
        self.qty_out = self.product_id.with_context({'location':stock_location}).outgoing_qty
        self.qty_diff = self.qty_available - self.qty
        self.qty_diff_vrt = self.qty_virtual - self.qty
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'explode_so_bom')
        sql="""drop table if exists explode_so_bom_config_lines;
        create table explode_so_bom_config_lines(id int, product_id int, product_uom_qty numeric);
        
        drop table if exists explode_so_bom_config;
        create table explode_so_bom_config(id int);
        
        drop FUNCTION IF EXISTS explode_so_range();
        CREATE OR REPLACE FUNCTION explode_so_range() 
        RETURNS TABLE (
        id INT,
        product_id INT,
        categ_id INT,
        uom_id INT,
        qty numeric
        )
        as $$
            BEGIN
            drop table if exists bom_all;
            create temp table bom_all as 
            select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.product_uom_qty) as product_qty 
            from explode_so_bom_config_lines as pqsol
            inner join mrp_bom mb on mb.product_id=pqsol.product_id 
            inner join mrp_bom_line mbl on mbl.bom_id=mb.id
            inner join product_product pp on pp.id=mbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            group by mbl.product_id,pt.categ_id,pt.uom_id;
            
            drop table if exists prd_ept;
            create temp table prd_ept as 
            select pp.id,pp.id as product_id,pt.categ_id,pt.uom_id,sum(pmbl.product_qty) as product_qty 
            from bom_all as pmbl
            inner join product_product pp on pp.id=pmbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            where pt.purchase_ok is False and pt.sale_ok is False and pt.can_be_expensed is False
            group by pp.id,pt.categ_id,pt.uom_id;
            
            drop table if exists bom_int;
            create temp table bom_int as 
            select * from bom_all 
            except 
            select * from prd_ept;
            
            drop table if exists bom_all;
            create temp table bom_all as 
            select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.product_qty) as product_qty 
            from prd_ept as pqsol
            inner join mrp_bom mb on mb.product_id=pqsol.product_id 
            inner join mrp_bom_line mbl on mbl.bom_id=mb.id
            inner join product_product pp on pp.id=mbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            group by mbl.product_id,pt.categ_id,pt.uom_id;
            
            drop table if exists prd_ept;
            create temp table prd_ept as 
            select pp.id,pp.id as product_id,pt.categ_id,pt.uom_id,sum(pmbl.product_qty) as product_qty 
            from bom_all as pmbl
            inner join product_product pp on pp.id=pmbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            where pt.purchase_ok is False and pt.sale_ok is False and pt.can_be_expensed is False
            group by pp.id,pt.categ_id,pt.uom_id;
            
            drop table if exists bom_fnl;
            create temp table bom_fnl as 
            select * from bom_all 
            except 
            select * from prd_ept;
            
            return query select * from bom_fnl 
            union 
            select * from bom_int 
            union 
            select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.product_qty) as product_qty 
            from prd_ept as pqsol
            inner join mrp_bom mb on mb.product_id=pqsol.product_id 
            inner join mrp_bom_line mbl on mbl.bom_id=mb.id
            inner join product_product pp on pp.id=mbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            group by mbl.product_id,pt.categ_id,pt.uom_id;
        END $$ 
        LANGUAGE 'plpgsql';
        
        CREATE OR REPLACE FUNCTION materials_to_sol(id_arg INTEGER)
        RETURNS TABLE (
         id INT
        )
        AS $$
         DECLARE
         iterar INTEGER :=1;
         BEGIN

         DROP TABLE IF EXISTS ept_pnd;
         CREATE TEMP TABLE ept_pnd(product_id INT);
         INSERT INTO ept_pnd VALUES (id_arg);

         DROP TABLE IF EXISTS purchase_fnl;
         CREATE TEMP TABLE purchase_fnl(product_id INT);

         WHILE iterar>0 LOOP
          DROP table IF EXISTS purchase_all;
          CREATE TEMP TABLE purchase_all AS
          SELECT mb.product_id 
          FROM mrp_bom_line mbl 
          INNER JOIN mrp_bom mb ON mb.id=mbl.bom_id 
          WHERE mbl.product_id in (select ept_pnd.product_id from ept_pnd)
          group by mbl.product_id,mbl.bom_id,mb.product_id;

          DROP table IF EXISTS ept_pnd;
          create temp table ept_pnd as
          select pa.product_id 
          from purchase_all pa 
          inner join product_product pp on pp.id=pa.product_id
          inner join product_template pt on pp.product_tmpl_id=pt.id
          where pt.purchase_ok is False and pt.sale_ok is False and pt.can_be_expensed is False;

          insert into purchase_fnl 
          select pa.product_id from purchase_all pa
          except 
          select ept_pnd.product_id from ept_pnd;
          SELECT count(ept_pnd.product_id) INTO iterar FROM ept_pnd;
         END LOOP;
         return query 
         select sol.id from 
         sale_order_line sol
         where sol.product_id in 
         (
          select purchase_fnl.product_id 
          from purchase_fnl 
          where purchase_fnl.product_id in (select bcl.product_id from explode_so_bom_config_lines bcl)
          group by purchase_fnl.product_id
         )
         and sol.order_id in (select * from explode_so_bom_config);
        END $$
        LANGUAGE 'plpgsql';
        
        create view explode_so_bom AS (
        select 
            esr.id as id,
            esr.product_id as product_id,
            esr.categ_id as categ_id,
            esr.uom_id as uom_id,
            esr.qty as qty
        from explode_so_range() as esr
        group by esr.id,product_id,esr.categ_id,esr.uom_id,esr.qty
        )"""
        
        self._cr.execute(sql)
        
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
    def button_view_sale_order_lines(self):
        sql="select * from materials_to_sol(%s)" % self.product_id.id
        self.env.cr.execute(sql)
        res_qry=self.env.cr.fetchall()
        ids_pol_proj=','.join(["%s"%j[0] for j in res_qry])
        return {
            'name': _('%s: %s')%(self.product_id.name, self.qty),
            'type': 'ir.actions.act_window',
            'views': [ (False ,'tree'),],
            'target': 'current',
            'domain': "[('id','in',(%s,))]"%ids_pol_proj,
            'res_model': 'sale.order.line.diff',
            'context': {'search_default_groupby_product': True, 'search_default_deliver_filter': True}
        }
