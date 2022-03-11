# -*- coding: utf-8 -*-
import logging
from openerp import api, fields, models, _
_logger = logging.getLogger(__name__)

class llamadas_isep(models.Model):
    _inherit = 'llamadas.isep'
    
    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        max_count_lim = contex.get('max_count_limit', False)
        _logger.debug("En read_group, max_count_limit vale "+max_count_lim)
        
        res = super(llamadas_isep, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, orderby, lazy)
        
        if max_count_lim:
            if lazy:
                fld=groupby[0]+'_count'
            else:
                fld='__count'
            col_
            for itm in res:
                if itm[fld]>max_count_lim:
                    if not lazy:
                        tmp={}
                        for i in itm.keys():
                            tmp[i]=False
                        tmp[fld]=0
                        res.append(tmp)
                    res.remove(itm)
            
        return res
