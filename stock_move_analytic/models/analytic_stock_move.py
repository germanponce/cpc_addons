# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import UserError, RedirectWarning, ValidationError

class ASM_StockLocation(models.Model):
    _inherit = 'stock.location'

    valuation_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account')


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
        if self.location_dest_id.valuation_in_account_id:
            try:
                res[0][2]['analytic_account_id'] = \
                self.location_dest_id.valuation_analytic_account_id and \
                self.location_dest_id.valuation_analytic_account_id.id or False
            except:
                return res
        return res


    # @api.v7
    # def _prepare_account_move_line(self,
    #                                cr,
    #                                uid,
    #                                move,
    #                                qty,
    #                                cost,
    #                                credit_account_id,
    #                                debit_account_id,
    #                                context=None):
    #     res = super(ASM_StockQuant, self)._prepare_account_move_line(
    #         cr,
    #         uid,
    #         move,
    #         qty,
    #         cost,
    #         credit_account_id,
    #         debit_account_id,
    #         context=context)

    #     if move.location_dest_id.valuation_in_account_id:
    #         res[0][2]['analytic_account_id'] = \
    #             move.location_dest_id.valuation_analytic_account_id and \
    #             move.location_dest_id.valuation_analytic_account_id.id or False

    #     return res

    # @api.v8
    # def _prepare_account_move_line(self,
    #                                move,
    #                                qty,
    #                                cost,
    #                                credit_account_id,
    #                                debit_account_id):
    #     res = super(ASM_StockQuant, self)._prepare_account_move_line(
    #         move,
    #         qty,
    #         cost,
    #         credit_account_id,
    #         debit_account_id)

    #     if move.location_dest_id.valuation_in_account_id:
    #         res[0][2]['account_analytic_id'] = \
    #             move.location_dest_id.valuation_analytic_account_id and \
    #             move.location_dest_id.valuation_analytic_account_id.id or False

    #     return res
