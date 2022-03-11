# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ExplodePOBoM(models.Model):
    _name = 'explode.mp.bom'
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
        sql="""
        drop table if exists explode_mp_bom_config;
        create table explode_mp_bom_config(id int);
        drop FUNCTION IF EXISTS explode_mp_ids();
        
        CREATE OR REPLACE FUNCTION explode_mp_ids() 
        RETURNS TABLE (
            id INT,
            product_id INT,
            categ_id INT,
            uom_id INT,
            qty numeric
        )
        as $$
            BEGIN
                    
            drop table if exists bom_mp_all;
            create temp table bom_mp_all as 
            select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.product_uom_qty) as product_qty 
            from (
                select mrpp.product_id as id, mrpp.product_id, sum(mrpp.product_qty) as product_uom_qty 
                from mrp_production mrpp
                where mrpp.id in (select cfg.id from explode_mp_bom_config cfg)
                group by mrpp.product_id
            ) as pqsol
            inner join mrp_bom mb on mb.product_id=pqsol.product_id 
            inner join mrp_bom_line mbl on mbl.bom_id=mb.id
            inner join product_product pp on pp.id=mbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            group by mbl.product_id,pt.categ_id,pt.uom_id;
                    
            drop table if exists prd_mp_ept;
            create temp table prd_mp_ept as 
            select pp.id,pp.id as product_id,pt.categ_id,pt.uom_id,sum(pmbl.product_qty) as product_qty 
            from bom_mp_all as pmbl
            inner join product_product pp on pp.id=pmbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            where pt.purchase_ok is False and pt.sale_ok is False and pt.can_be_expensed is False
            group by pp.id,pt.categ_id,pt.uom_id;
            
            drop table if exists bom_mp_fnl;
            create temp table bom_mp_fnl as 
            select * from bom_mp_all 
            except 
            select * from prd_mp_ept;
            
            return query select * from bom_mp_fnl 
            union 
            select mbl.product_id as id,mbl.product_id,pt.categ_id,pt.uom_id,sum(mbl.product_qty*pqsol.product_qty) as product_qty 
            from prd_mp_ept as pqsol
            inner join mrp_bom mb on mb.product_id=pqsol.product_id 
            inner join mrp_bom_line mbl on mbl.bom_id=mb.id
            inner join product_product pp on pp.id=mbl.product_id
            inner join product_template pt on pp.product_tmpl_id=pt.id
            group by mbl.product_id,pt.categ_id,pt.uom_id;
        
        END $$ 
        LANGUAGE 'plpgsql';
        
        create view explode_mp_bom AS (
        select 
            esr.id as id,
            esr.product_id as product_id,
            esr.categ_id as categ_id,
            esr.uom_id as uom_id,
            esr.qty as qty
        from explode_mp_ids() as esr
        group by esr.id,product_id,esr.categ_id,esr.uom_id,esr.qty
        )
        """
        
        self._cr.execute(sql)
