# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools

class InvoiceAnalysisWizard(models.TransientModel):
    _inherit = 'argil.invoice.analysis.wizard'
    
    @api.multi
    def show_analysis(self):
        res=super(InvoiceAnalysisWizard, self).show_analysis()
        res['context']='{"search_default_no_overdue": 1, "search_default_groupby_currency":1,"search_default_groupby_customer":1,"search_default_no_apo":1}'
        res['target']='main'
        return res
