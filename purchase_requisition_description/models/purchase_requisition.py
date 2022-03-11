# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
import pytz
from odoo import tools

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"
    
    description = fields.Char(string='Description')
    
class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    
    @api.multi
    def action_in_progress(self):
        super(PurchaseRequisition, self).action_in_progress()
        #VSGTN: El usuario pudiera no tener configurada la zona horaria
        utz=pytz.timezone(self.env.user.tz)
        date=tools.datetime.now(utz)
        date_utc=date.astimezone(pytz.UTC)
        dow=int(date_utc.strftime("%w"))
        dias=2
        if dow>3:
            dias+=2
        elif dow == 6:
            dias+=1
        time_delta=tools.timedelta(days=dias)
        self.write({'date_end': date_utc+time_delta})
