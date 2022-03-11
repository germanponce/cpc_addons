# -*- coding: utf-8 -*-

import models
        
def purge_db_aux(cr,registry):
    sql="""
    drop table if exists explode_mp_bom_config;
    drop view if exists explode_mp_bom;
    drop function if exists explode_mp_ids();
    """
    cr.execute(sql);
