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
import os
import shutil

class IrCron(models.Model):
    _name = 'ir.cron'
    _inherit ='ir.cron'

    import_path_doc = fields.Char('Ruta Importacion', size=128)
    import_path_done_doc = fields.Char('Ruta Importacion Procesados', size=128)

    @api.multi
    def clean_messages(self):
        for rec in self:
            if rec.message_ids:
                rec.message_ids.unlink()

    

class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit ='account.journal'

    @api.depends('name','code')
    @api.multi
    def _get_name_computed(self):
        for rec in self:
            journal_upper_name = rec.name.replace(' ','')
            journal_upper_name = journal_upper_name.upper()
            rec.journal_upper_name = journal_upper_name

    ### Nombre sin Espacios y en Mayusculas  ### 
    journal_upper_name = fields.Char(string='Nombre sin Espacios', compute='_get_name_computed', readonly=True, store=True)



class AccountMove(models.Model):
    _name = 'account.move'
    _inherit ='account.move'

    is_imported = fields.Boolean('Importada')

    fiscal_uuid = fields.Char('UUID Fiscal', size=128, copy=False, readonly=True)

    journal_name = fields.Char('Nombre del Diario', size=128, copy=False, readonly=True)

    def import_automatically_moves(self):
        cron_obj = self.env['ir.cron']
        context = dict(self.env.context)

        da_list = []
        document_csv = ""
        salto_line = "\n"
        sp = ","
        cron_prog_id = cron_obj.search([('function','=','import_automatically_moves')])
        import_path_doc = ""
        import_path_done_doc = ""
        move_obj = self.env['account.move']
        invoice_obj = self.env['account.invoice']
        ### Marcar estas Polizas como omited_search=True
        if cron_prog_id:
            import_path_doc = cron_prog_id[0].import_path_doc
            import_path_done_doc = cron_prog_id[0].import_path_done_doc
            if not import_path_doc or not import_path_done_doc:
                cron_plan_id = cron_prog_id[0]
                cron_plan_export_log = "<strong><h4>Error en la Importacion</h4></strong><br/><strong>Fecha: "+str(fields.Datetime.now())+"</strong><br/><br/><strong>Error:</strong/><br/>"+"No se configuro correctamente los directorios para Importar las Polizas de Proveedores."
                cron_plan_id.message_post(body=str(cron_plan_export_log))
                return True
            if import_path_doc[-1] != '/':
                import_path_doc = import_path_doc+'/'
            if import_path_done_doc[-1] != '/':
                import_path_done_doc = import_path_done_doc+'/'

        final_document_list_to_write = []

        ## Marcar las Polizas con este Campo: omited_search ###
        try:
            files_to_be_imported = [ f for f in os.listdir(import_path_doc) if os.path.isfile(os.path.join(import_path_doc,f)) ]
            files_to_be_imported = files_to_be_imported[0:5]
            for xfile in files_to_be_imported:                
                x = 0
                move_lines = []
                move_vals = {

                }
                try:
                    f = open(os.path.join(import_path_doc,xfile),'r').read().replace('\r', '')
                    partner_id = False
                    date_move = ""
                    sat_uuid = ""
                    move_reference = ""
                    for line in f.split('\n'):
                        if x == 0:
                            x+=1
                            continue                    
                        data = line.split(',')
                        if data:
                            if len(data) > 1:
                                if x == 1:
                                    ## Headers Account Move
                                    journal_name = data[0]
                                    journal_id = False
                                    if journal_name:
                                        self.env.cr.execute("""
                                            select id from account_journal
                                                where UPPER(name) = %s;
                                            """,(journal_name.upper(),))
                                        cr_res = self.env.cr.fetchall()
                                        if cr_res:
                                            journal_id = cr_res[0][0]
                                    if not journal_id:
                                        self.env.cr.execute("""
                                            select id from account_journal
                                                where UPPER(journal_upper_name) = %s;
                                            """,(journal_name.upper().replace(' ',''),))
                                        cr_res = self.env.cr.fetchall()
                                        if cr_res:
                                            journal_id = cr_res[0][0]

                                    date_move =  data[1]  
                                    period_name = data[2]
                                    period_id = False
                                    if period_name:
                                        self.env.cr.execute("""
                                            select id from account_period
                                                where UPPER(name) = %s;
                                            """,(period_name.upper(),))
                                        cr_res = self.env.cr.fetchall()
                                        if cr_res:
                                            period_id = cr_res[0][0]

                                    reference = data[3]
                                    move_vals.update({
                                            'journal_id': journal_id,
                                            'ref': reference,
                                            'date': date_move,
                                            'period_id': period_id,
                                            'is_imported': True,
                                            'omited_search': True,
                                            'journal_name': journal_name,
                                        })
                                    ### Move Lines 
                                    sat_uuid = data[5]
                                    move_reference = data[4]
                                    move_name = data[6]
                                    account_code = data[7]
                                    account_id = False
                                    if account_code:
                                        self.env.cr.execute("""
                                            select id from account_account
                                                where UPPER(code) = %s;
                                            """,(account_code.upper(),))
                                        cr_res = self.env.cr.fetchall()
                                        if cr_res:
                                            account_id = cr_res[0][0]
                                    # partner_name =  data[6]
                                    partner_id = data[8]
                                    credit = data[10]
                                    debit = data[9]

                                    try:
                                        credit = float(credit)
                                    except:
                                        credit = 0.0
                                    try:
                                        debit = float(debit)
                                    except:
                                        debit = 0.0
                                    xline = (0,0, {
                                            'account_id': account_id,
                                            'name': move_name,
                                            'partner_id': partner_id,
                                            'date_maturity': date_move,
                                            'credit': credit,
                                            'debit': debit,
                                        })
                                    move_lines.append(xline)

                                else:
                                    ### Move Lines 
                                    move_name = data[6]
                                    account_code = data[7]
                                    account_id = False
                                    if account_code:
                                        self.env.cr.execute("""
                                            select id from account_account
                                                where UPPER(code) = %s;
                                            """,(account_code.upper(),))
                                        cr_res = self.env.cr.fetchall()
                                        if cr_res:
                                            account_id = cr_res[0][0]
                                    # partner_name =  data[6]
                                    partner_id = data[8]
                                    credit = data[10]
                                    debit = data[9]

                                    try:
                                        credit = float(credit)
                                    except:
                                        credit = 0.0
                                    try:
                                        debit = float(debit)
                                    except:
                                        debit = 0.0
                                    xline = (0,0, {
                                            'account_id': account_id,
                                            'name': move_name,
                                            'partner_id': partner_id,
                                            'date_maturity': date_move,
                                            'credit': credit,
                                            'debit': debit,
                                        })
                                    move_lines.append(xline)

                        x+=1
                    move_vals.update({
                        'line_ids': move_lines,
                        'partner_id': partner_id,
                        'fiscal_uuid': sat_uuid, 
                        })
                    ## Creando la Tupla para recorrerla mas Adelante ##
                    final_document_list_to_write.append((move_vals,str(xfile)))
                except Exception, e:
                    error = tools.ustr(traceback.format_exc())
                    cron_plan_id = cron_prog_id[0]
                    cron_plan_export_log = "<strong><h4>Error en la Importacion y Conciliacion.</h4></strong><br/><strong>Fecha: "+str(fields.Datetime.now())+"</strong><br/><br/><strong>Error:</strong/><br/>"+str(error)+"<br/><strong>Archivo:</strong><br/>"+xfile
                    cron_plan_id.message_post(body=str(cron_plan_export_log))

        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            cron_plan_id = cron_prog_id[0]
            cron_plan_export_log = cron_plan_id.export_log
            cron_plan_export_log = "<strong><h4>Error en la Importacion y Conciliacion.</h4></strong><br/><strong>Fecha: "+str(fields.Datetime.now())+"</strong><br/><br/><strong>Error:</strong/><br/>"+str(error)
            # cron_plan_id.write({'export_log':cron_plan_export_log})
            # self._cr.execute("""
            #     update ir_cron set export_log=%s where id=%s;
            #     """,(cron_plan_export_log,cron_plan_id.id,))
            cron_plan_id.message_post(body=str(cron_plan_export_log))

        for document in final_document_list_to_write:
            try:
                vals = document[0]
                file_readed = document[1]
                if not vals['journal_id']:
                    error = "No se encontro un Diario en Odoo con el Nombre %s para la creacion del Asiento" % vals['journal_name']
                    cron_plan_id = cron_prog_id[0]
                    cron_plan_export_log = "<strong><h4>Error en la Importacion y Conciliacion.</h4></strong><br/><strong>Fecha: "+str(fields.Datetime.now())+"</strong><br/><br/><strong>Error:</strong/><br/>"+str(error)+"<br/><strong>Archivo:</strong><br/>"+file_readed
                    cron_plan_id.message_post(body=str(cron_plan_export_log))
                    continue
                move_id = move_obj.sudo().create(vals)

                move_id.post()
                if move_id.fiscal_uuid:
                    invoice_id  = invoice_obj.search([('fiscal_uuid','=',move_id.fiscal_uuid)])
                    if invoice_id:
                        invoice  = invoice_id[0]
                        amls_to_reconcile = self.env['account.move.line']
                        for move_line in move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable')):
                            amls_to_reconcile += move_line
                        amls_to_reconcile += invoice.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
                        amls_to_reconcile.reconcile(writeoff_acc_id=False, writeoff_journal_id=False)

                shutil.move(os.path.join(import_path_doc,file_readed),os.path.join(import_path_done_doc,file_readed))
            except:
                file_readed = document[1]
                error = tools.ustr(traceback.format_exc())
                cron_plan_id = cron_prog_id[0]
                cron_plan_export_log = cron_plan_id.export_log
                cron_plan_export_log = "<strong><h4>Error en la Importacion y Conciliacion.</h4></strong><br/><strong>Fecha: "+str(fields.Datetime.now())+"</strong><br/><br/><strong>Error:</strong/><br/>"+str(error)+"<br/><strong>Archivo: </strong/>"+file_readed

            # Mover de Ubicacion los Archivos Procesados
            # shutil.move(os.path.join(import_path_doc,xfile),os.path.join(import_path_done_doc,xfile))

        return True