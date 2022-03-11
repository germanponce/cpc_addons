# -*- coding: utf-8 -*-

import wizard
import models

def set_defaults(cr,registry):
    from odoo.api import Environment, SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})
    stock_location=env['stock.location'].search([('name','like','AMP')])
    stock_location=stock_location.child_ids.filtered(lambda x: x.name == 'Stock')
    if stock_location:
        env['ir.values'].sudo().set_default('purchase.config.settings', 'stock_location', stock_location.id)
        
def purge_db_aux(cr,registry):
    from odoo.api import Environment, SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})
    purchase_menu=env.ref('purchase.menu_purchase_root')
    purchase_menu_rpt=env.ref('purchase.purchase_report')
    purchase_menu_rpt.parent_id=purchase_menu.id
    sql="""
    drop table if exists explode_so_bom_config;
    drop view if exists explode_so_bom;
    drop function if exists explode_so_range();
    """
    cr.execute(sql);
