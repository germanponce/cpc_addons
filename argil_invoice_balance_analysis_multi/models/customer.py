# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools, release

class account_invoice_customer_collection_projection(models.Model):
    _inherit = 'account.invoice.customer_collection_projection'

    argil_sql_str=""" create or replace view account_invoice_customer_collection_projection as (                                                                                                            
                SELECT l.id as id, l.partner_id as partner_id, res_partner.name as "partner_name",
                  ai.type invoice_type, ai.user_id, ai.company_id,
                    CASE WHEN ai.id is not null THEN ai.date_due ElSE l.date_maturity END as "date_due",
                    days_due*-1 as "avg_days_overdue", 
                    l.date as "oldest_invoice_date",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END as "total",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN 01 AND  %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_01to30", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND  %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_31to60", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND  %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_61to90", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_91to120",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and days_due >= %s and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_121togr",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and days_due <= 0 and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END as "current",
                    CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                    ai.number as "ref",
                    ai.id as "invoice_id", ai.comment, ai.currency_id
                   
                 FROM account_move_line as l     
                INNER JOIN         
                  (SELECT lt.id, 
                   CASE WHEN inv.date_due is null then 0
                   WHEN inv.id is not null THEN EXTRACT(DAY FROM (inv.date_due - now())) 
                   ELSE EXTRACT(DAY FROM (lt.date_maturity - now())) END AS days_due             
                   FROM account_move_line lt 
            LEFT JOIN account_invoice inv on lt.move_id = inv.move_id
           WHERE lt.account_id in (select id from account_account acc where acc.internal_type = 'receivable')
            ) DaysDue       
            ON DaysDue.id = l.id               
                 
                INNER JOIN account_account ON account_account.id = l.account_id and account_account.internal_type='receivable' and not account_account.deprecated 
                INNER JOIN res_company ON account_account.company_id = res_company.id             
                INNER JOIN account_move ON account_move.id = l.move_id and account_move.state = 'posted'
                INNER JOIN account_invoice as ai ON ai.move_id = l.move_id           
                INNER JOIN res_partner ON res_partner.id = l.partner_id  
                WHERE not l.reconciled
                  AND days_due IS NOT NULL
                  and (l.amount_residual <> 0 or l.amount_residual_currency <> 0));
              """

    if release.major_version == "9.0":
    
        def init(self, cr):
            context = self._context
            for_customer_menu = False
            for_overdue = False
            if 'for_customer_menu' in context:
                for_customer_menu = context['for_customer_menu']
            if 'for_overdue' in context:
                for_overdue = context['for_overdue']

            # self._table = account_invoice_supplier_collection_projection            
            # self.env['ir.values'].sudo().set_default('account.config.settings', 'days_limit_projection', 30)
            self._init_sql_view(cr)
            
    elif release.major_version == "10.0":
        
        @api.model_cr
        def init(self):
            context = self._context
            for_customer_menu = False
            for_overdue = False
            if 'for_customer_menu' in context:
                for_customer_menu = context['for_customer_menu']
            if 'for_overdue' in context:
                for_overdue = context['for_overdue']

            # self._table = account_invoice_supplier_collection_projection
            # self.env['ir.values'].sudo().set_default('account.config.settings', 'days_limit_projection', 30)
            self._init_sql_view(self.env.cr)
            
    def _init_sql_view(self, cr):

        ## Actualizacion de Facturas que no tienen Fecha de Vencimiento ### 
        self.env.cr.execute("""
          update account_invoice set date_due=account_move_line.date_maturity
            from account_move_line where account_move_line.move_id = account_invoice.move_id
             and account_invoice.state not in ('draft','cancel') and account_invoice.date_due is null;
          """)

        context = self._context
        for_customer_menu = False
        for_overdue = False
        if 'for_customer_menu' in context:
            for_customer_menu = context['for_customer_menu']
        if 'for_overdue' in context:
            for_overdue = context['for_overdue']


        tools.drop_view_if_exists(cr, self._table)
        dlp = self.env['ir.values'].get_default('account.config.settings', 'days_limit_projection')
        if dlp:
            # print "### QUERY >>>> ",self.argil_sql_str % (dlp, dlp+1, dlp*2, dlp*2+1, dlp*3, dlp*3+1, dlp*4, dlp*4+1)
            cr.execute(self.argil_sql_str % (dlp, dlp+1, dlp*2, dlp*2+1, dlp*3, dlp*3+1, dlp*4, dlp*4+1))

    @api.model
    def load_views(self, views, options=None):
        res=super(account_invoice_customer_collection_projection, self).load_views(views, options)
        dlp = self.env['ir.values'].get_default('account.config.settings', 'days_limit_projection')
        res['fields_views']['list']['fields']['days_due_01to30']['string']="1 - %s" % (dlp)
        res['fields_views']['list']['fields']['days_due_31to60']['string']="%s - %s" % (dlp+1, dlp*2)
        res['fields_views']['list']['fields']['days_due_61to90']['string']="%s - %s" % (dlp*2+1, dlp*3)
        res['fields_views']['list']['fields']['days_due_91to120']['string']="%s - %s" % (dlp*3+1, dlp*4)
        res['fields_views']['list']['fields']['days_due_121togr']['string']="+ %s" % (dlp*4+1)
        return res


class account_invoice_customer_balance_due(models.Model):
    _inherit = 'account.invoice.customer_balance_due'

    argil_sql_str_for_overdue = """ create or replace view account_invoice_customer_balance_due as (                                                                                                            
                SELECT l.id as id, l.partner_id as partner_id, res_partner.name as "partner_name",
                  ai.type invoice_type, ai.user_id, ai.company_id,
                    CASE WHEN ai.id is not null and ai.date_due is not null THEN ai.date_due ElSE l.date_maturity END as "date_due",
                    days_due*-1 as "avg_days_overdue", 
                    l.date as "oldest_invoice_date",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END as "total",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN 01 AND  %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_01to30", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND  %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_31to60", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND  %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_61to90", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND %s) and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_91to120",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and days_due >= %s and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_121togr",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and days_due <= 0 and ai.id is not null THEN
                            CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END as "current",
                    CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                    ai.number as "ref",
                    ai.id as "invoice_id", ai.comment, ai.currency_id
                   
                 FROM account_move_line as l     
                INNER JOIN         
                  (SELECT lt.id, 
                   CASE WHEN inv.date_due is null then 0
                   WHEN inv.id is not null THEN EXTRACT(DAY FROM (now() - inv.date_due)) 
                   ELSE EXTRACT(DAY FROM (now() - lt.date_maturity)) END AS days_due             
                   FROM account_move_line lt 
            LEFT JOIN account_invoice inv on lt.move_id = inv.move_id
           WHERE lt.account_id in (select id from account_account acc where acc.internal_type = 'receivable')
            ) DaysDue       
            ON DaysDue.id = l.id               
                 
                INNER JOIN account_account ON account_account.id = l.account_id and account_account.internal_type='receivable' and not account_account.deprecated 
                INNER JOIN res_company ON account_account.company_id = res_company.id             
                INNER JOIN account_move ON account_move.id = l.move_id and account_move.state = 'posted'
                INNER JOIN account_invoice as ai ON ai.move_id = l.move_id           
                INNER JOIN res_partner ON res_partner.id = l.partner_id  
                WHERE not l.reconciled
                  AND days_due IS NOT NULL
                  and (l.amount_residual <> 0 or l.amount_residual_currency <> 0));
              """

    if release.major_version == "9.0":
    
        def init(self, cr):
            context = self._context
            for_customer_menu = False
            for_overdue = False
            if 'for_customer_menu' in context:
                for_customer_menu = context['for_customer_menu']
            if 'for_overdue' in context:
                for_overdue = context['for_overdue']

            # self._table = account_invoice_supplier_collection_projection            
            # self.env['ir.values'].sudo().set_default('account.config.settings', 'days_limit_projection', 30)
            self._init_sql_view(cr)
            
    elif release.major_version == "10.0":
        
        @api.model_cr
        def init(self):
            context = self._context
            for_customer_menu = False
            for_overdue = False
            if 'for_customer_menu' in context:
                for_customer_menu = context['for_customer_menu']
            if 'for_overdue' in context:
                for_overdue = context['for_overdue']

            # self._table = account_invoice_supplier_collection_projection
            # self.env['ir.values'].sudo().set_default('account.config.settings', 'days_limit_projection', 30)
            self._init_sql_view(self.env.cr)
            
    def _init_sql_view(self, cr):

        ## Actualizacion de Facturas que no tienen Fecha de Vencimiento ### 
        self.env.cr.execute("""
          update account_invoice set date_due=account_move_line.date_maturity
            from account_move_line where account_move_line.move_id = account_invoice.move_id
             and account_invoice.state not in ('draft','cancel') and account_invoice.date_due is null;
          """)

        context = self._context
        for_customer_menu = False
        for_overdue = False
        if 'for_customer_menu' in context:
            for_customer_menu = context['for_customer_menu']
        if 'for_overdue' in context:
            for_overdue = context['for_overdue']

        tools.drop_view_if_exists(cr, self._table)
        dlp = self.env['ir.values'].get_default('account.config.settings', 'days_limit_projection')
        if dlp:
            # print "### QUERY >>>> ",self.argil_sql_str % (dlp, dlp+1, dlp*2, dlp*2+1, dlp*3, dlp*3+1, dlp*4, dlp*4+1)
            cr.execute(self.argil_sql_str_for_overdue % (dlp, dlp+1, dlp*2, dlp*2+1, dlp*3, dlp*3+1, dlp*4, dlp*4+1))
        


    @api.model
    def load_views(self, views, options=None):
        res=super(account_invoice_customer_balance_due, self).load_views(views, options)
        dlp = self.env['ir.values'].get_default('account.config.settings', 'days_limit_projection')
        res['fields_views']['list']['fields']['days_due_01to30']['string']="1 - %s" % (dlp)
        res['fields_views']['list']['fields']['days_due_31to60']['string']="%s - %s" % (dlp+1, dlp*2)
        res['fields_views']['list']['fields']['days_due_61to90']['string']="%s - %s" % (dlp*2+1, dlp*3)
        res['fields_views']['list']['fields']['days_due_91to120']['string']="%s - %s" % (dlp*3+1, dlp*4)
        res['fields_views']['list']['fields']['days_due_121togr']['string']="+ %s" % (dlp*4+1)
        return res
