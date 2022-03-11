# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


from odoo import models, fields, api, _, tools
from datetime import time, datetime
from odoo import SUPERUSER_ID
from odoo import tools
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import time
from odoo.tools.translate import _

import traceback

import tempfile
import base64

class IrCron(models.Model):
    _name = 'ir.cron'
    _inherit = ['mail.thread', 'ir.cron']

    path_doc = fields.Char('Ruta Exportacion', size=128)
    export_log = fields.Text('Log Exportacion', copy=False)

class invoice_fit(models.Model):
    _inherit = 'account.invoice'

    fiscal_uuid = fields.Char('UUID Fiscal', size=128, copy=False, track_visibility="onchange", readonly=True)


class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit ='account.journal'

    individual_export = fields.Boolean('CSV Individual', help='El proceso de Exportacion creara un Archivo por Asiento Contable.', )


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit ='account.move'

    is_exported = fields.Boolean('Exportada')
    omited_search = fields.Boolean('Omitir en Importacion/Exportacion')

    def export_automatically_moves(self):
        cron_obj = self.env['ir.cron']
        context = dict(self.env.context)
        moves_not_exported = self.search([('is_exported','=',False),('omited_search','=',False)])
        if not moves_not_exported:
            return True
        da_list = []
        document_csv = ""
        salto_line = "\n"
        sp = ","
        cron_prog_id = cron_obj.search([('function','=','export_automatically_moves')])
        path_doc = ""
        if cron_prog_id:
            path_doc = cron_prog_id[0].path_doc
            if path_doc[-1] != '/':
                path_doc = path_doc+'/'
        if not path_doc:
            cron_plan_id = cron_prog_id[0]
            cron_plan_export_log = "<strong><h4>Error en la Exportacion</h4></strong><br/><strong>Fecha: "+str(fields.Datetime.now())+"</strong><br/><br/><strong>Error:</strong/><br/>"+"No se configuro un directorio para colocar las Polizas Exportadas."
            cron_plan_id.message_post(body=str(cron_plan_export_log))
            return True
        # cabeceras_l = "Nombre"+","+"Referencia"+","+"Diario"+","+\
        # "Fecha"+","+"Periodo"+","+"Movimientos/Empresa"+","+"Movimientos/Fecha"+","+"Movimientos/Fecha Vencimiento"+\
        # ","+"Movimientos/Cuenta"+","+"Movimientos/Debe"+","+"Movimientos/Haber"

        cabeceras_l= "Diario"+","+"Fecha"+","+"Periodo"+","+"Referencia"+","+"Compra"+","+"UUID" +","+"Concepto para la poliza"+","+"Cuenta Contable"+","+"ID Prov"+","+"Cargo"+","+"Abono"

        document_csv = document_csv+cabeceras_l

        final_document_list_to_write = []
        try:
            moves_not_exported_wo_journal_individual = self.search([('is_exported','=',False),('journal_id.individual_export','=',False),('omited_search','=',False)])
            if moves_not_exported_wo_journal_individual:
                for move in moves_not_exported_wo_journal_individual:
                    move_name = move.name
                    move_ref = move.ref if move.ref else ""
                    journal_name = move.journal_id.name if move.journal_id else ""
                    move_date = move.date if move.date else ""
                    if move_date:
                        move_date_split = move_date.split('-')
                        move_date = move_date_split[2]+'-'+move_date_split[1]+'-'+move_date_split[0]
                    period_name = move.period_id.name if move.period_id else ""
                    uuid = ""
                    compra = ""
                    picking_list = [x.stock_move_id for x in move.line_ids if x.stock_move_id]
                    if picking_list:
                        picking_list = [x.picking_id for x in picking_list if x.picking_id]
                        compra = picking_list[0].purchase_id.name if picking_list[0].purchase_id else ""
                    if not compra:
                        invoice_list = [x.invoice_id for x in move.line_ids if x.invoice_id]
                        if invoice_list:
                            compra = invoice_list[0].purchase_id.name if invoice_list[0].purchase_id else ""
                            uuid  = invoice_list[0].fiscal_uuid if invoice_list[0].fiscal_uuid else ""
                            if not compra:
                                compra = invoice_list[0].origin if invoice_list[0].origin  else ""

                    move_val = journal_name.replace(',','')+","+move_date.replace(',','')+","+period_name.replace(',','')+","+move_ref.replace(',','')+","+compra.replace(',','-')+","+uuid.replace(',','')
                    document_csv = document_csv+salto_line+move_val
                    m = 0
                    move_line_val = ""
                    for mvl in move.line_ids:
                        if m == 0:
                            move_line_val = ""
                            partner_id = str(mvl.partner_id.id) if mvl.partner_id else ""
                            date_line = mvl.date
                            if date_line:
                                date_line_split = date_line.split('-')
                                date_line = date_line_split[2]+'-'+date_line_split[1]+'-'+date_line_split[0]
                            date_end_line = mvl.date_maturity
                            if date_end_line:
                                date_end_line_split = date_end_line.split('-')
                                date_end_line = date_end_line_split[2]+'-'+date_end_line_split[1]+'-'+date_end_line_split[0]
                            account_name = mvl.account_id.name if mvl.account_id else ""
                            if account_name:
                                #ccount_name = mvl.account_id.code+" "+account_name
                                account_name = mvl.account_id.code
                            debit_amount = mvl.debit
                            credit_amount = mvl.credit
                            move_line_name = mvl.name

                            move_line_val = ","+move_line_name.replace(',','')+","+account_name.replace(',','')+","+partner_id+","+str(debit_amount)+","+str(credit_amount)
                            document_csv = document_csv+move_line_val
                        else:
                            move_line_val = ",,,,,,"
                            partner_id = str(mvl.partner_id.id) if mvl.partner_id else ""
                            date_line = mvl.date
                            if date_line:
                                date_line_split = date_line.split('-')
                                date_line = date_line_split[2]+'-'+date_line_split[1]+'-'+date_line_split[0]
                            date_end_line = mvl.date_maturity
                            if date_end_line:
                                date_end_line_split = date_end_line.split('-')
                                date_end_line = date_end_line_split[2]+'-'+date_end_line_split[1]+'-'+date_end_line_split[0]
                            account_name = mvl.account_id.name if mvl.account_id else ""
                            if account_name:
                                #account_name = mvl.account_id.code+" "+account_name
                                account_name = mvl.account_id.code
                            debit_amount = mvl.debit
                            credit_amount = mvl.credit

                            move_line_name = mvl.name

                            move_line_val = move_line_val+move_line_name.replace(',','')+","+account_name.replace(',','')+","+partner_id+","+str(debit_amount)+","+str(credit_amount)
                            #document_csv = document_csv+move_line_val

                            document_csv = document_csv+salto_line+move_line_val
                        m+=1
                    move.write({'is_exported':True})
                    # detalle_lineas = ""
                    # for linea in consult_br.preinventory_lines:
                    #     linea_str = ""
                    #     if linea.product_id:
                    #         linea_str = str(linea.location_id.name)+","+str(linea.product_id.default_code)+\
                    #         ","+str(linea.qty)+","+str(linea.uom_id.name)+","+str(linea.prod_lot_id.name if linea.prod_lot_id else linea.prod_lot)
                       
                    #     detalle_lineas = detalle_lineas+salto_line+linea_str
                    # document_csv = document_csv+detalle_lineas+salto_line+salto_line
                if document_csv:
                    date = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
                    datas_fname = "Polizas Contables "+str(date)+".csv" # Nombre del Archivo
                    # file_write = open(path_doc+datas_fname,'w')
                    # file_write.write(document_csv)

                    document_val = {
                        'datas_fname': datas_fname,
                        'datas': document_csv,
                    }
                    final_document_list_to_write.append(document_val)


            ### Diarios con Movimiento Individual ###
            moves_exported_with_journal_individual = self.search([('is_exported','=',False),('journal_id.individual_export','=',True),('omited_search','=',False)])

            if moves_exported_with_journal_individual:
                cons=0
                for move in moves_exported_with_journal_individual:
                    cabeceras_l= "Diario"+","+"Fecha"+","+"Periodo"+","+"Referencia"+","+"Compra"+","+"UUID" +","+"Concepto para la poliza"+","+"Cuenta Contable"+","+"ID Prov"+","+"Cargo"+","+"Abono"
                    document_csv = ""+cabeceras_l

                    move_name = move.name
                    move_ref = move.ref if move.ref else ""
                    journal_name = move.journal_id.name if move.journal_id else ""
                    move_date = move.date if move.date else ""
                    if move_date:
                        move_date_split = move_date.split('-')
                        move_date = move_date_split[2]+'-'+move_date_split[1]+'-'+move_date_split[0]
                    period_name = move.period_id.name if move.period_id else ""
                    uuid = ""
                    compra = ""
                    picking_list = [x.stock_move_id for x in move.line_ids if x.stock_move_id]
                    if picking_list:
                        picking_list = [x.picking_id for x in picking_list if x.picking_id]
                        compra = picking_list[0].purchase_id.name if picking_list[0].purchase_id else ""
                    if not compra:
                        invoice_list = [x.invoice_id for x in move.line_ids if x.invoice_id]
                        if invoice_list:
                            compra = invoice_list[0].purchase_id.name if invoice_list[0].purchase_id else ""
                            uuid  = invoice_list[0].fiscal_uuid if invoice_list[0].fiscal_uuid else ""
                            if not compra:
                                compra = invoice_list[0].origin if invoice_list[0].origin else ""
                    # print "########## >>>> ",journal_name
                    # print "########## >>>> ",move_date
                    # print "########## >>>> ",period_name
                    # print "########## >>>> ",move_ref
                    # print "########## >>>> ",compra
                    # print "########## >>>> ",uuid
                    move_val = journal_name.replace(',','')+","+move_date+","+period_name.replace(',','')+","+move_ref.replace(',','')+","+compra.replace(',','-')+","+uuid.replace(',','')
                    document_csv = document_csv+salto_line+move_val
                    m = 0
                    move_line_val = ""
                    for mvl in move.line_ids:
                        if m == 0:
                            move_line_val = ""
                            partner_name = mvl.partner_id.name if mvl.partner_id else ""
                            partner_id = str(mvl.partner_id.id) if mvl.partner_id else ""
                            date_line = mvl.date
                            if date_line:
                                date_line_split = date_line.split('-')
                                date_line = date_line_split[2]+'-'+date_line_split[1]+'-'+date_line_split[0]
                            date_end_line = mvl.date_maturity
                            if date_end_line:
                                date_end_line_split = date_end_line.split('-')
                                date_end_line = date_end_line_split[2]+'-'+date_end_line_split[1]+'-'+date_end_line_split[0]
                            account_name = mvl.account_id.name if mvl.account_id else ""
                            if account_name:
                                #account_name = mvl.account_id.code+" "+account_name
                                account_name = mvl.account_id.code
                            debit_amount = mvl.debit
                            credit_amount = mvl.credit
                            move_line_name = mvl.name

                            move_line_val = ","+move_line_name+","+account_name+","+partner_id+","+str(debit_amount)+","+str(credit_amount)
                            document_csv = document_csv+move_line_val
                        else:
                            move_line_val = ",,,,,,"
                            partner_name = mvl.partner_id.name if mvl.partner_id else ""
                            partner_id = str(mvl.partner_id.id) if mvl.partner_id else ""
                            date_line = mvl.date
                            if date_line:
                                date_line_split = date_line.split('-')
                                date_line = date_line_split[2]+'-'+date_line_split[1]+'-'+date_line_split[0]
                            date_end_line = mvl.date_maturity
                            if date_end_line:
                                date_end_line_split = date_end_line.split('-')
                                date_end_line = date_end_line_split[2]+'-'+date_end_line_split[1]+'-'+date_end_line_split[0]
                            account_name = mvl.account_id.name if mvl.account_id else ""
                            if account_name:
                                #account_name = mvl.account_id.code+" "+account_name
                                account_name = mvl.account_id.code
                            debit_amount = mvl.debit
                            credit_amount = mvl.credit

                            move_line_name = mvl.name

                            move_line_val = move_line_val+move_line_name.replace(',','')+","+account_name.replace(',','')+","+partner_id+","+str(debit_amount)+","+str(credit_amount)
                            #document_csv = document_csv+move_line_val

                            document_csv = document_csv+salto_line+move_line_val
                        m+=1
                    move.write({'is_exported':True})
                    # detalle_lineas = ""
                    # for linea in consult_br.preinventory_lines:
                    #     linea_str = ""
                    #     if linea.product_id:
                    #         linea_str = str(linea.location_id.name)+","+str(linea.product_id.default_code)+\
                    #         ","+str(linea.qty)+","+str(linea.uom_id.name)+","+str(linea.prod_lot_id.name if linea.prod_lot_id else linea.prod_lot)
                       
                    #     detalle_lineas = detalle_lineas+salto_line+linea_str
                    # document_csv = document_csv+detalle_lineas+salto_line+salto_line
                    if document_csv:
                        cons+=1
                        date = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
                        datas_fname = "Poliza Contable - "+move.journal_id.name+" 0"+str(cons)+" -"+str(date)+".csv" # Nombre del Archivo
                        # file_write = open(path_doc+datas_fname,'w')
                        # file_write.write(document_csv)
                        document_val = {
                            'datas_fname': datas_fname,
                            'datas': document_csv,
                        }
                        final_document_list_to_write.append(document_val)


        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            cron_plan_id = cron_prog_id[0]
            cron_plan_export_log = cron_plan_id.export_log
            cron_plan_export_log = "<strong><h4>Error en la Exportacion</h4></strong><br/><strong>Fecha: "+str(fields.Datetime.now())+"</strong><br/><br/><strong>Error:</strong/><br/>"+str(error)
            # cron_plan_id.write({'export_log':cron_plan_export_log})
            # self._cr.execute("""
            #     update ir_cron set export_log=%s where id=%s;
            #     """,(cron_plan_export_log,cron_plan_id.id,))
            moves_not_exported.write({'is_exported':False})
            cron_plan_id.message_post(body=str(cron_plan_export_log))
        
        ## Grabando el Resultado Final ##
        if final_document_list_to_write:
            for document in final_document_list_to_write:
                datas_fname = document['datas_fname']
                datas = document['datas']
                file_write = open(path_doc+datas_fname,'w')
                file_write.write(datas)

        return True
