# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import pytz

class PurchaseOrder(models.Model):
    _inherit = "sale.order"
    
    @api.one
    def _get_state_translation(self):
        fld='state'
        idx=[y[0] for y in self._fields[fld].selection].index(self.state)
        tr_rs=self.env['ir.translation']
        self.state_str = tr_rs.search([('type', '=', 'selection'),
                                ('name','=',self._name+','+fld),
                                ('source','=',self._fields[fld].selection[idx][1])]).value
        
    state_str = fields.Char(compute='_get_state_translation')
    
    @api.model
    def track_pending(self):
        utz=pytz.timezone(self.env.context.get('tz',False) or 'America/Mexico_City')
        date=tools.datetime.now(utz)
        date=utz.localize(tools.datetime(date.year, date.month, date.day))
        date=date.astimezone(pytz.UTC)
        days=self.env['ir.values'].get_default('sale.state.config', 'days_notif')
        lim_sup=date-tools.timedelta(days-1)
        lim_inf=date-tools.timedelta(days+1)
        #Para lectura de campo
        #for i in so:
        # if pytz.UTC.localize(tools.datetime.strptime(i.confirmation_date,tools.DEFAULT_SERVER_DATETIME_FORMAT))<limit:
        #  print i.confirmation_date
        # Verificar. https://books.google.com.mx/books?id=4Qe5DQAAQBAJ&pg=PP6&lpg=PP6&dq=odoo+_notify+method&source=bl&ots=v30C8NCSae&sig=0Ufsvm_eZUhr7XluxA2xLsKiMj8&hl=es-419&sa=X&ved=0ahUKEwjLsondtLjaAhVFQq0KHV6dBREQ6AEIXzAG#v=onepage&q=odoo%20_notify%20method&f=false
        itms=self.search([('confirmation_date','>',lim_inf.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                          ('confirmation_date','<',lim_sup.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                          ('state','not in',('done','cancel'))])
        if itms:
            emails = self.env['mail.mail']
            tplt_cstm=self.env['mail.template'].browse(self.env['ir.values'].get_default('sale.state.config', 'customer_template'))
            tplt_agnt=self.env['mail.template'].browse(self.env['ir.values'].get_default('sale.state.config', 'agent_template'))
            for itm in itms:
                email_msg=tplt_cstm.generate_email(itm.id, fields=['body_html', 'subject'])
                email_msg['recipient_ids']=[(4, itm.partner_id.id)]
                email=emails.create(email_msg)
                emails|=email
                email_msg=tplt_agnt.generate_email(itm.id, fields=['body_html', 'subject'])
                email_msg['recipient_ids']=[(4, itm.user_id.partner_id.id)]
                email=emails.create(email_msg)
                emails|=email
                emails.send()
        days=self.env['ir.values'].get_default('sale.state.config', 'days_late')
        lim_sup=date-tools.timedelta(days-1)
        lim_inf=date-tools.timedelta(days+1)
        itms=self.search([('confirmation_date','>',lim_inf.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                          ('confirmation_date','<',lim_sup.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                          ('state','not in',('done','cancel'))])
        if itms:
            emails = self.env['mail.mail']
            tplt_agnt=self.env['mail.template'].browse(self.env['ir.values'].get_default('sale.state.config', 'agent_late_template'))
            for itm in itms:
                email_msg=tplt_agnt.generate_email(itm.id, fields=['body_html', 'subject'])
                email_msg['recipient_ids']=[(4, itm.user_id.partner_id.id)]
                email=emails.create(email_msg)
                emails|=email
                emails.send()
        return True