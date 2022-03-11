# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools, release

class account_invoice_supplier_collection_projection(models.Model):
    _inherit = 'account.invoice.supplier_collection_projection'
    
    payment_ord_id = fields.Many2one('account.payment.order', string='Payment Order')
    
    argil_sql_str = """
                create or replace view account_invoice_supplier_collection_projection as (
SELECT l.id as id, l.partner_id as partner_id, res_partner.name as "partner_name",
                  ai.type invoice_type, ai.user_id, ai.company_id,
                    CASE WHEN ai.id is not null THEN ai.date_due ElSE l.date_maturity END as "date_due",
                    -1*days_due as "avg_days_overdue", 
                    l.date as "oldest_invoice_date",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and ai.id is not null THEN
                            -1*CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END as "total",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN 01 AND  %s) and ai.id is not null THEN
                            -1*CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_01to30", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND  %s) and ai.id is not null THEN
                            -1*CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_31to60", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND  %s) and ai.id is not null THEN
                            -1*CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_61to90", 
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and (days_due BETWEEN %s AND %s) and ai.id is not null THEN
                            -1*CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_91to120",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and days_due >= %s and ai.id is not null THEN
                            -1*CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END AS "days_due_121togr",
                    CASE WHEN (l.amount_residual <> 0 or l.amount_residual_currency <> 0) and days_due <= 0 and ai.id is not null THEN
                            -1*CASE WHEN l.amount_residual_currency <> 0.0 THEN l.amount_residual_currency ELSE l.amount_residual END 
                         ELSE 0.0
                         END as "current",
                    CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                    ai.reference as "ref",
                    ai.id as "invoice_id", ai.comment, ai.currency_id, ai.payment_ord_id 
                   
                 FROM account_move_line as l     
                INNER JOIN         
                  (SELECT lt.id, 
                   CASE WHEN inv.date_due is null then 0
                   WHEN inv.id is not null THEN EXTRACT(DAY FROM (inv.date_due - now())) 
                   ELSE EXTRACT(DAY FROM (lt.date_maturity - now())) END AS days_due             
                   FROM account_move_line lt 
            LEFT JOIN account_invoice inv on lt.move_id = inv.move_id
           WHERE lt.account_id in (select id from account_account acc where acc.internal_type = 'payable')
            ) DaysDue       
            ON DaysDue.id = l.id               
                 
                INNER JOIN account_account ON account_account.id = l.account_id and account_account.internal_type='payable' and not account_account.deprecated 
                INNER JOIN res_company ON account_account.company_id = res_company.id             
                INNER JOIN account_move ON account_move.id = l.move_id and account_move.state = 'posted'
                INNER JOIN account_invoice as ai ON ai.move_id = l.move_id           
                INNER JOIN res_partner ON res_partner.id = l.partner_id  
                WHERE not l.reconciled
                  AND days_due IS NOT NULL
                  and (l.amount_residual <> 0 or l.amount_residual_currency <> 0));
            """
