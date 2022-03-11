# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
####### TRABAJAR CON LOS EXCEL
import xlsxwriter

import tempfile

from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

import base64

from odoo.exceptions import UserError, RedirectWarning, ValidationError


import sys
reload(sys)  
sys.setdefaultencoding('utf8')


class InvoiceAnalysisWizard(models.TransientModel):
    _name = 'argil.invoice.analysis.wizard'
    
    days_limit_projection = fields.Selection([(7, 'Semanal'), (30, 'Mensual')], required=True, string='Rango Proyeccion Columnas', 
                                           help='Days for every column width.')


    datas_fname = fields.Char('File Name',size=256)
    file = fields.Binary('Layout')
    download_file = fields.Boolean('Descargar Archivo', default=False)
    cadena_decoding = fields.Text('Binario sin encoding')
    type = fields.Selection([('xlsx','Excel')], 'Tipo Exportacion', 
                            required=False, default="xlsx")


    @api.model
    def default_get(self, default_fields):
        res = super(InvoiceAnalysisWizard, self).default_get(default_fields)
        res['days_limit_projection'] = self.env['ir.values'].get_default('account.config.settings', 'days_limit_projection')
        return res
    
    @api.multi
    def show_analysis(self):
        context = self._context

        for_customer_menu = False
        for_overdue = False
        if 'for_customer_menu' in context:
            for_customer_menu = context['for_customer_menu']
        if 'for_overdue' in context:
            for_overdue = context['for_overdue']

        if for_overdue == False:
            model = 'account.invoice.supplier_collection_projection' if self.env.context.get('for_supplier_menu') else 'account.invoice.customer_collection_projection'
            self.env['ir.values'].sudo().set_default('account.config.settings', 'days_limit_projection', self.days_limit_projection)
            self.env[model]._init_sql_view(self.env.cr)
            name = "Payment Projection" if self.env.context.get('for_supplier_menu') else 'Collection Projection'
            view_id = self.env.ref('argil_invoice_balance_analysis.view_account_invoice_supplier_collection_projection_tree').id if self.env.context.get('for_supplier_menu') else self.env.ref('argil_invoice_balance_analysis.view_account_invoice_customer_collection_projection_tree').id
            return {
                'name'      : _(name),
                'view_type' : 'list',
                'view_mode' : 'list',
                'view_id'   : [view_id],
                'res_model' : model,
                'context'   : '{"search_default_no_overdue": 1, "search_default_groupby_currency":1,"search_default_groupby_customer":1}',
                'type'      : 'ir.actions.act_window',
            }
        else:
            model = 'account.invoice.supplier_balance_due' if self.env.context.get('for_supplier_menu') else 'account.invoice.customer_balance_due'
            self.env['ir.values'].sudo().set_default('account.config.settings', 'days_limit_projection', self.days_limit_projection)
            self.env[model]._init_sql_view(self.env.cr)
            name = "Payment Projection" if self.env.context.get('for_supplier_menu') else 'Collection Projection'
            view_id = self.env.ref('argil_invoice_balance_analysis.view_account_invoice_supplier_balance_due_tree').id if self.env.context.get('for_supplier_menu') else self.env.ref('argil_invoice_balance_analysis.view_account_invoice_customer_balance_due_tree').id
            return {
                'name'      : _(name),
                'view_type' : 'list',
                'view_mode' : 'list',
                'view_id'   : [view_id],
                'res_model' : model,
                'context'   : '{"search_default_overdue":1,"search_default_groupby_currency":1,"search_default_groupby_customer":1}',
                'type'      : 'ir.actions.act_window',
            }

        
    @api.multi
    def export_xlsx(self):
        context = self._context
        invoice_obj = self.env['account.invoice'].sudo()
        partner_obj = self.env['res.partner'].sudo()
        for_customer_menu = False
        for_overdue = False
        if 'for_customer_menu' in context:
            for_customer_menu = context['for_customer_menu']
        if 'for_overdue' in context:
            for_overdue = context['for_overdue']

        model = ""
        if for_overdue == False:
            model = 'account.invoice.supplier_collection_projection' if self.env.context.get('for_supplier_menu') else 'account.invoice.customer_collection_projection'

        else:
            model = 'account.invoice.supplier_balance_due' if self.env.context.get('for_supplier_menu') else 'account.invoice.customer_balance_due'
        model_obj = self.env[model].sudo()

        ### Recreando las Vistas ####
        cr = self.env.cr
        self.env['ir.values'].sudo().set_default('account.config.settings', 'days_limit_projection', self.days_limit_projection)
        model_obj._init_sql_view(cr)

        model_ids = model_obj.search([])

        if not model_ids:
            raise ValidationError("Error!\nNo existe informacion para generar el Excel.")
        report_name = ""
        report_customer_collection = False # Proyeccion Clientes
        report_customer_due = False # Saldos Vencidos Clientes
        report_supplier_collection = False # Proyeccion Proveedores
        report_supplier_due = False # Saldos Vencidos Proveedores
        if model == 'account.invoice.supplier_collection_projection' :
            report_supplier_collection = True
            report_name = "Proyeccion de Cobranza Proveedores"
        elif model == 'account.invoice.customer_collection_projection':
            report_name = "Proyeccion de Cobranza Clientes"
            report_customer_collection = True
        elif model == 'account.invoice.supplier_balance_due':
            report_name = "Saldos Vencidos Proveedores"
            report_supplier_due = True
        else:
            report_name = "Saldos Vencidos Clientes"
            report_customer_due = True

        ### Comenzamos con el Excel ####
        ### Creacion del Documento ####
        fname=tempfile.NamedTemporaryFile(suffix='.xlsx',delete=False)

        workbook = xlsxwriter.Workbook(fname)

        ### Creacion de los Estilos ###

        format_period_title = workbook.add_format({
                                'bold':     True,
                                'align':    'center',
                                'valign':   'vcenter',
                            })

        format_period_title.set_font_size(18)


        format_black_ct_center = workbook.add_format({'bold': True})
        format_black_ct_center.set_font_size(13)
        format_black_ct_center.set_align('center_across')


        format_bold_center_normal = workbook.add_format({
                                'bold':     True,
                                'align':    'center',
                                'valign':   'vcenter',
                            })

        format_bold = workbook.add_format({
                                'bold':     True
                            })

        format_simple_money = workbook.add_format()
        format_simple_money.set_num_format('$#,##0.00')


        ### Modelo a Tabla ###
        model_to_table = model.replace('.','_')
        
        self.env.cr.execute("""
            select currency_id from """+ model_to_table+ """ group by currency_id ;""" )
        cr_res = self.env.cr.fetchall()

        currency_list = [x[0] for x in cr_res]

        if currency_list:
            company_br = self.env.user.company_id
            for currency in currency_list:
                currency_br = self.env['res.currency'].browse(currency)

                ## Creando la Pagina ####
                worksheet_resumen = workbook.add_worksheet(currency_br.name.upper())
                worksheet_resumen.merge_range('A1:K2', company_br.name.upper(),format_period_title)

                saldo_global_sum = 0.0
                valor_historico_global_sum = 0.0
                valor_actual_global_sum = 0.0

                subtitle_report = ""
                if report_customer_collection:
                    subtitle_report = "CUENTAS POR COBRAR POR FECHA DE VENCIMIENTO MONEDA : "+currency_br.name.upper()+" AL "+str(fields.Date.context_today(self))
                if report_customer_due:
                    subtitle_report = "CUENTAS A COBRAR VENCIDAS POR MONEDA : "+currency_br.name.upper()+" AL "+str(fields.Date.context_today(self))
                if report_supplier_collection:
                    subtitle_report = "CUENTAS POR PAGAR POR FECHA DE VENCIMIENTO MONEDA : "+currency_br.name.upper()+" AL "+str(fields.Date.context_today(self))
                if report_supplier_due:
                    subtitle_report = "CUENTAS A PAGAR VENCIDAS POR MONEDA : "+currency_br.name.upper()+" AL "+str(fields.Date.context_today(self))
                
                ### Leyenda Tipo de Reporte ###
                worksheet_resumen.merge_range('A3:K3', subtitle_report,format_black_ct_center)

                ### Columnas utilizadas para los Valores ####
                headers_values_list = ['A','B','C','D','E','F','G','H','I','J','K']
                worksheet_resumen.set_column('A:K', 16)
                ### Cabeceras del Reporte ####
                worksheet_resumen.write(headers_values_list[0]+'5',"Empesa",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[1]+'5',"Documento",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[2]+'5',"F. Factura",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[3]+'5',"F. Vencimiento",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[4]+'5',"Referencia",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[5]+'5',"Moneda",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[6]+'5',"TC Fact",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[7]+'5',"Saldo",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[8]+'5',"Valor Historico",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[9]+'5',"TC Reporte",format_bold_center_normal)
                worksheet_resumen.write(headers_values_list[10]+'5',"Valor Actual",format_bold_center_normal)

                # model_currency_record_ids = model_obj.search([('currency_id','=',currency)])  
                # print "########## model_currency_record_ids >>>> ",model_currency_record_ids

                ### Agrupando los Registros por Periodo de Vencimiento ###
                days_due_01to30 = False
                days_due_31to60 = False
                days_due_61to90 = False
                days_due_91to120 = False
                days_due_121togr = False

                dlp = self.days_limit_projection
                days_due_01to30_period_str = "1 - %s" % (dlp)
                days_due_31to60_period_str = "%s - %s" % (dlp+1, dlp*2)
                days_due_61to90_period_str = "%s - %s" % (dlp*2+1, dlp*3)
                days_due_91to120_period_str = "%s - %s" % (dlp*3+1, dlp*4)
                days_due_121togr_period_str = "+ %s" % (dlp*4+1)

                i = 6

                self.env.cr.execute("""
                    select id from """+ model_to_table+ """ where days_due_01to30 > 0.0  and currency_id = %s;""",(currency, ) )

                # print "######### QUERY >>> ","""
                #     select id from """+ model_to_table+ """ where days_due_01to30 > 0.0  and currency_id = %s;""",(currency, )

                cr_res = self.env.cr.fetchall()
                days_due_01to30 = [x[0] for x in cr_res if x]
                # print "#########  days_due_01to30 >>> ",days_due_01to30

                if days_due_01to30:
                    saldo_sum = 0.0
                    valor_historico_sum = 0.0
                    valor_actual_sum = 0.0
                    for record in model_obj.browse(days_due_01to30):
                        self.env.cr.execute("""
                            select invoice_id, days_due_01to30, partner_id, date_due
                               from """+ model_to_table+ """ where id = %s ;""" % (record.id,) )
                        record_res = self.env.cr.fetchall()

                        ## ORM no puede hacer un browse record de una Clase tipo Vista ###
                        record_invoice_id = record_res[0][0] if record_res[0][0] else False
                        record_days_due_01to30 = record_res[0][1] if record_res[0][1] else 0.0
                        record_partner_id = record_res[0][2] if record_res[0][2] else False
                        record_date_due = record_res[0][3] if record_res[0][3] else ""

                        tc = 1
                        tc_impresion = 1
                        currency_name = currency_br.name
                        invoice_br = invoice_obj.browse(record_invoice_id)
                        partner_br = partner_obj.browse(record_partner_id)
                        if currency_name.upper() != 'MXN':
                            date_invoice = invoice_br.date_invoice if invoice_br else record_date_due
                            rate = currency_br.with_context({'date': date_invoice}).rate
                            rate = rate != 0 and 1.0/rate or 0.0
                            tc = rate

                            date_now = fields.Date.context_today(self)
                            rate2 = currency_br.with_context({'date': date_now}).rate
                            rate2 = rate2 != 0 and 1.0/rate2 or 0.0
                            tc_impresion = rate2
                        
                        ### Asignacion de Valores ###
                        saldo = record_days_due_01to30
                        valor_historico = saldo * tc
                        valor_actual = saldo * tc_impresion

                        #### Acumulacion de la Asignacion ####
                        saldo_sum += saldo
                        valor_historico_sum += valor_historico
                        valor_actual_sum += valor_actual

                        worksheet_resumen.write(headers_values_list[0]+str(i), partner_br.name if partner_br else "")
                        worksheet_resumen.write(headers_values_list[1]+str(i), invoice_br.number if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[2]+str(i), invoice_br.date_invoice if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[3]+str(i), record_date_due if record_date_due else "")
                        worksheet_resumen.write(headers_values_list[4]+str(i), invoice_br.name if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[5]+str(i), currency_name.upper())
                        worksheet_resumen.write(headers_values_list[6]+str(i), tc, format_simple_money)
                        worksheet_resumen.write(headers_values_list[7]+str(i), saldo, format_simple_money)
                        worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico, format_simple_money)
                        worksheet_resumen.write(headers_values_list[9]+str(i), tc_impresion, format_simple_money)
                        worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual, format_simple_money)

                        ## Incremento Contador ##
                        i+=1

                    ### Acumulando los Valores Globales ###
                    saldo_global_sum += saldo_sum
                    valor_historico_global_sum += valor_historico_sum
                    valor_actual_global_sum += valor_actual_sum

                    ### Grabando los Totales ###
                    worksheet_resumen.write(headers_values_list[0]+str(i), "Total de Vencimientos "+days_due_01to30_period_str, format_bold)
                    worksheet_resumen.write(headers_values_list[7]+str(i), saldo_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual_sum, format_simple_money)
                    ## Incremento Contador ##
                    i+=1


                self.env.cr.execute("""
                    select id from """+ model_to_table+ """ where days_due_31to60 > 0.0  and currency_id = %s;""",(currency, ) )

                # print "######### QUERY >>> ","""
                #     select id from """+ model_to_table+ """ where days_due_31to60 > 0.0  and currency_id = %s;""",(currency, )

                cr_res = self.env.cr.fetchall()
                days_due_31to60 = [x[0] for x in cr_res if x]
                # print "#########  days_due_31to60 >>> ",days_due_31to60

                if days_due_31to60:
                    ## Incremento Contador ##
                    i+=1

                    saldo_sum = 0.0
                    valor_historico_sum = 0.0
                    valor_actual_sum = 0.0
                    for record in model_obj.browse(days_due_31to60):
                        self.env.cr.execute("""
                            select invoice_id, days_due_31to60, partner_id, date_due
                               from """+ model_to_table+ """ where id = %s ;""" % (record.id,) )
                        record_res = self.env.cr.fetchall()

                        ## ORM no puede hacer un browse record de una Clase tipo Vista ###
                        record_invoice_id = record_res[0][0] if record_res[0][0] else False
                        record_days_due_31to60 = record_res[0][1] if record_res[0][1] else 0.0
                        record_partner_id = record_res[0][2] if record_res[0][2] else False
                        record_date_due = record_res[0][3] if record_res[0][3] else ""

                        tc = 1
                        tc_impresion = 1
                        currency_name = currency_br.name
                        invoice_br = invoice_obj.browse(record_invoice_id)
                        partner_br = partner_obj.browse(record_partner_id)
                        if currency_name.upper() != 'MXN':
                            date_invoice = invoice_br.date_invoice if invoice_br else record_date_due
                            rate = currency_br.with_context({'date': date_invoice}).rate
                            rate = rate != 0 and 1.0/rate or 0.0
                            tc = rate

                            date_now = fields.Date.context_today(self)
                            rate2 = currency_br.with_context({'date': date_now}).rate
                            rate2 = rate2 != 0 and 1.0/rate2 or 0.0
                            tc_impresion = rate2
                        
                        ### Asignacion de Valores ###
                        saldo = record_days_due_31to60
                        valor_historico = saldo * tc
                        valor_actual = saldo * tc_impresion

                        #### Acumulacion de la Asignacion ####
                        saldo_sum += saldo
                        valor_historico_sum += valor_historico
                        valor_actual_sum += valor_actual

                        worksheet_resumen.write(headers_values_list[0]+str(i), partner_br.name if partner_br else "")
                        worksheet_resumen.write(headers_values_list[1]+str(i), invoice_br.number if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[2]+str(i), invoice_br.date_invoice if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[3]+str(i), record_date_due if record_date_due else "")
                        worksheet_resumen.write(headers_values_list[4]+str(i), invoice_br.name if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[5]+str(i), currency_name.upper())
                        worksheet_resumen.write(headers_values_list[6]+str(i), tc, format_simple_money)
                        worksheet_resumen.write(headers_values_list[7]+str(i), saldo, format_simple_money)
                        worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico, format_simple_money)
                        worksheet_resumen.write(headers_values_list[9]+str(i), tc_impresion, format_simple_money)
                        worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual, format_simple_money)

                        ## Incremento Contador ##
                        i+=1

                    ### Acumulando los Valores Globales ###
                    saldo_global_sum += saldo_sum
                    valor_historico_global_sum += valor_historico_sum
                    valor_actual_global_sum += valor_actual_sum

                    ### Grabando los Totales ###
                    worksheet_resumen.write(headers_values_list[0]+str(i), "Total de Vencimientos "+days_due_31to60_period_str, format_bold)
                    worksheet_resumen.write(headers_values_list[7]+str(i), saldo_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual_sum, format_simple_money)
                    ## Incremento Contador ##
                    i+=1

                self.env.cr.execute("""
                    select id from """+ model_to_table+ """ where days_due_61to90 > 0.0  and currency_id = %s;""",(currency, ) )
                
                # print "######### QUERY >>> ","""
                #     select id from """+ model_to_table+ """ where days_due_61to90 > 0.0  and currency_id = %s;""",(currency, )

                cr_res = self.env.cr.fetchall()
                days_due_61to90 = [x[0] for x in cr_res if x]
                # print "#########  days_due_61to90 >>> ",days_due_61to90

                if days_due_61to90:
                    ## Incremento Contador ##
                    i+=1

                    saldo_sum = 0.0
                    valor_historico_sum = 0.0
                    valor_actual_sum = 0.0
                    for record in model_obj.browse(days_due_61to90):
                        self.env.cr.execute("""
                            select invoice_id, days_due_61to90, partner_id, date_due
                               from """+ model_to_table+ """ where id = %s ;""" % (record.id,) )
                        record_res = self.env.cr.fetchall()

                        ## ORM no puede hacer un browse record de una Clase tipo Vista ###
                        record_invoice_id = record_res[0][0] if record_res[0][0] else False
                        record_days_due_61to90 = record_res[0][1] if record_res[0][1] else 0.0
                        record_partner_id = record_res[0][2] if record_res[0][2] else False
                        record_date_due = record_res[0][3] if record_res[0][3] else ""

                        tc = 1
                        tc_impresion = 1
                        currency_name = currency_br.name
                        invoice_br = invoice_obj.browse(record_invoice_id)
                        partner_br = partner_obj.browse(record_partner_id)
                        if currency_name.upper() != 'MXN':
                            date_invoice = invoice_br.date_invoice if invoice_br else record_date_due
                            rate = currency_br.with_context({'date': date_invoice}).rate
                            rate = rate != 0 and 1.0/rate or 0.0
                            tc = rate

                            date_now = fields.Date.context_today(self)
                            rate2 = currency_br.with_context({'date': date_now}).rate
                            rate2 = rate2 != 0 and 1.0/rate2 or 0.0
                            tc_impresion = rate2
                        
                        ### Asignacion de Valores ###
                        saldo = record_days_due_61to90
                        valor_historico = saldo * tc
                        valor_actual = saldo * tc_impresion

                        #### Acumulacion de la Asignacion ####
                        saldo_sum += saldo
                        valor_historico_sum += valor_historico
                        valor_actual_sum += valor_actual

                        worksheet_resumen.write(headers_values_list[0]+str(i), partner_br.name if partner_br else "")
                        worksheet_resumen.write(headers_values_list[1]+str(i), invoice_br.number if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[2]+str(i), invoice_br.date_invoice if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[3]+str(i), record_date_due if record_date_due else "")
                        worksheet_resumen.write(headers_values_list[4]+str(i), invoice_br.name if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[5]+str(i), currency_name.upper())
                        worksheet_resumen.write(headers_values_list[6]+str(i), tc, format_simple_money)
                        worksheet_resumen.write(headers_values_list[7]+str(i), saldo, format_simple_money)
                        worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico, format_simple_money)
                        worksheet_resumen.write(headers_values_list[9]+str(i), tc_impresion, format_simple_money)
                        worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual, format_simple_money)

                        ## Incremento Contador ##
                        i+=1

                    ### Acumulando los Valores Globales ###
                    saldo_global_sum += saldo_sum
                    valor_historico_global_sum += valor_historico_sum
                    valor_actual_global_sum += valor_actual_sum

                    ### Grabando los Totales ###
                    worksheet_resumen.write(headers_values_list[0]+str(i), "Total de Vencimientos "+days_due_61to90_period_str, format_bold)
                    worksheet_resumen.write(headers_values_list[7]+str(i), saldo_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual_sum, format_simple_money)
                    ## Incremento Contador ##
                    i+=1

                self.env.cr.execute("""
                    select id from """+ model_to_table+ """ where days_due_91to120 > 0.0  and currency_id = %s;""",(currency, ) )

                # print "######### QUERY >>> ","""
                #     select id from """+ model_to_table+ """ where days_due_91to120 > 0.0  and currency_id = %s;""",(currency, )

                cr_res = self.env.cr.fetchall()
                days_due_91to120 = [x[0] for x in cr_res if x]
                # print "#########  days_due_91to120 >>> ",days_due_91to120

                if days_due_91to120:
                    ## Incremento Contador ##
                    i+=1

                    saldo_sum = 0.0
                    valor_historico_sum = 0.0
                    valor_actual_sum = 0.0
                    for record in model_obj.browse(days_due_91to120):
                        self.env.cr.execute("""
                            select invoice_id, days_due_91to120, partner_id, date_due
                               from """+ model_to_table+ """ where id = %s ;""" % (record.id,) )
                        record_res = self.env.cr.fetchall()

                        ## ORM no puede hacer un browse record de una Clase tipo Vista ###
                        record_invoice_id = record_res[0][0] if record_res[0][0] else False
                        record_days_due_91to120 = record_res[0][1] if record_res[0][1] else 0.0
                        record_partner_id = record_res[0][2] if record_res[0][2] else False
                        record_date_due = record_res[0][3] if record_res[0][3] else ""

                        tc = 1
                        tc_impresion = 1
                        currency_name = currency_br.name
                        invoice_br = invoice_obj.browse(record_invoice_id)
                        partner_br = partner_obj.browse(record_partner_id)
                        if currency_name.upper() != 'MXN':
                            date_invoice = invoice_br.date_invoice if invoice_br else record_date_due
                            rate = currency_br.with_context({'date': date_invoice}).rate
                            rate = rate != 0 and 1.0/rate or 0.0
                            tc = rate

                            date_now = fields.Date.context_today(self)
                            rate2 = currency_br.with_context({'date': date_now}).rate
                            rate2 = rate2 != 0 and 1.0/rate2 or 0.0
                            tc_impresion = rate2
                        
                        ### Asignacion de Valores ###
                        saldo = record_days_due_91to120
                        valor_historico = saldo * tc
                        valor_actual = saldo * tc_impresion

                        #### Acumulacion de la Asignacion ####
                        saldo_sum += saldo
                        valor_historico_sum += valor_historico
                        valor_actual_sum += valor_actual

                        worksheet_resumen.write(headers_values_list[0]+str(i), partner_br.name if partner_br else "")
                        worksheet_resumen.write(headers_values_list[1]+str(i), invoice_br.number if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[2]+str(i), invoice_br.date_invoice if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[3]+str(i), record_date_due if record_date_due else "")
                        worksheet_resumen.write(headers_values_list[4]+str(i), invoice_br.name if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[5]+str(i), currency_name.upper())
                        worksheet_resumen.write(headers_values_list[6]+str(i), tc, format_simple_money)
                        worksheet_resumen.write(headers_values_list[7]+str(i), saldo, format_simple_money)
                        worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico, format_simple_money)
                        worksheet_resumen.write(headers_values_list[9]+str(i), tc_impresion, format_simple_money)
                        worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual, format_simple_money)

                        ## Incremento Contador ##
                        i+=1

                    ### Acumulando los Valores Globales ###
                    saldo_global_sum += saldo_sum
                    valor_historico_global_sum += valor_historico_sum
                    valor_actual_global_sum += valor_actual_sum

                    ### Grabando los Totales ###
                    worksheet_resumen.write(headers_values_list[0]+str(i), "Total de Vencimientos "+days_due_91to120_period_str, format_bold)
                    worksheet_resumen.write(headers_values_list[7]+str(i), saldo_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual_sum, format_simple_money)
                    ## Incremento Contador ##
                    i+=1

                self.env.cr.execute("""
                    select id from """+ model_to_table+ """ where days_due_121togr > 0.0  and currency_id = %s;""",(currency, ) )
                
                # print "######### QUERY >>> ","""
                #     select id from """+ model_to_table+ """ where days_due_121togr > 0.0  and currency_id = """+str(currency)+""" ;""" 

                cr_res = self.env.cr.fetchall()
                days_due_121togr = [x[0] for x in cr_res if x]
                # print "#########  days_due_121togr >>> ",days_due_121togr

                if days_due_121togr:
                    ## Incremento Contador ##
                    i+=1

                    saldo_sum = 0.0
                    valor_historico_sum = 0.0
                    valor_actual_sum = 0.0
                    for record in model_obj.browse(days_due_121togr):
                        self.env.cr.execute("""
                            select invoice_id, days_due_121togr, partner_id, date_due
                               from """+ model_to_table+ """ where id = %s ;""" % (record.id,) )
                        record_res = self.env.cr.fetchall()

                        ## ORM no puede hacer un browse record de una Clase tipo Vista ###
                        record_invoice_id = record_res[0][0] if record_res[0][0] else False
                        record_days_due_121togr = record_res[0][1] if record_res[0][1] else 0.0
                        record_partner_id = record_res[0][2] if record_res[0][2] else False
                        record_date_due = record_res[0][3] if record_res[0][3] else ""

                        tc = 1
                        tc_impresion = 1
                        currency_name = currency_br.name
                        invoice_br = invoice_obj.browse(record_invoice_id)
                        partner_br = partner_obj.browse(record_partner_id)
                        if currency_name.upper() != 'MXN':
                            date_invoice = invoice_br.date_invoice if invoice_br else record_date_due
                            rate = currency_br.with_context({'date': date_invoice}).rate
                            rate = rate != 0 and 1.0/rate or 0.0
                            tc = rate

                            date_now = fields.Date.context_today(self)
                            rate2 = currency_br.with_context({'date': date_now}).rate
                            rate2 = rate2 != 0 and 1.0/rate2 or 0.0
                            tc_impresion = rate2
                        
                        ### Asignacion de Valores ###
                        saldo = record_days_due_121togr
                        valor_historico = saldo * tc
                        valor_actual = saldo * tc_impresion

                        #### Acumulacion de la Asignacion ####
                        saldo_sum += saldo
                        valor_historico_sum += valor_historico
                        valor_actual_sum += valor_actual

                        worksheet_resumen.write(headers_values_list[0]+str(i), partner_br.name if partner_br else "")
                        worksheet_resumen.write(headers_values_list[1]+str(i), invoice_br.number if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[2]+str(i), invoice_br.date_invoice if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[3]+str(i), record_date_due if record_date_due else "")
                        worksheet_resumen.write(headers_values_list[4]+str(i), invoice_br.name if invoice_br else "")
                        worksheet_resumen.write(headers_values_list[5]+str(i), currency_name.upper())
                        worksheet_resumen.write(headers_values_list[6]+str(i), tc, format_simple_money)
                        worksheet_resumen.write(headers_values_list[7]+str(i), saldo, format_simple_money)
                        worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico, format_simple_money)
                        worksheet_resumen.write(headers_values_list[9]+str(i), tc_impresion, format_simple_money)
                        worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual, format_simple_money)

                        ## Incremento Contador ##
                        i+=1

                    ### Acumulando los Valores Globales ###
                    saldo_global_sum += saldo_sum
                    valor_historico_global_sum += valor_historico_sum
                    valor_actual_global_sum += valor_actual_sum

                    ### Grabando los Totales ###
                    worksheet_resumen.write(headers_values_list[0]+str(i), "Total de Vencimientos "+days_due_121togr_period_str, format_bold)
                    worksheet_resumen.write(headers_values_list[7]+str(i), saldo_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico_sum, format_simple_money)
                    worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual_sum, format_simple_money)
                    ## Incremento Contador ##
                    i+=1

                ### Grabando las sumatorias Globales ###
                i+=1
                worksheet_resumen.write(headers_values_list[0]+str(i), "Sumas en "+currency_br.name.upper(), format_bold)
                worksheet_resumen.write(headers_values_list[7]+str(i), saldo_global_sum, format_simple_money)
                worksheet_resumen.write(headers_values_list[8]+str(i), valor_historico_global_sum, format_simple_money)
                worksheet_resumen.write(headers_values_list[10]+str(i), valor_actual_global_sum, format_simple_money)

                records_overdue  = False
                records_no_overdue  = False
                if report_customer_due == True:
                    self.env.cr.execute("""
                        select id from """+ model_to_table+ """ where current > 0.0  and currency_id = %s;""",(currency, ) )
                    cr_res = self.env.cr.fetchall()
                    records_overdue = [x[0] for x in cr_res if x]

                if report_supplier_due == True:
                    self.env.cr.execute("""
                        select id from """+ model_to_table+ """ where current > 0.0  and currency_id = %s;""",(currency, ) )
                    cr_res = self.env.cr.fetchall()
                    records_overdue = [x[0] for x in cr_res if x]
                    # print "#########  records_overdue >>> ",records_overdue

                if report_customer_collection:
                    self.env.cr.execute("""
                        select id from """+ model_to_table+ """ where current <= 0.0  and currency_id = %s;""",(currency, ) )
                    cr_res = self.env.cr.fetchall()
                    records_no_overdue = [x[0] for x in cr_res if x]
                    # print "#########  records_no_overdue >>> ",records_no_overdue

                if report_supplier_collection:
                    self.env.cr.execute("""
                        select id from """+ model_to_table+ """ where current <= 0.0  and currency_id = %s;""",(currency, ) )
                    cr_res = self.env.cr.fetchall()
                    records_no_overdue = [x[0] for x in cr_res if x]
                    # print "#########  records_no_overdue >>> ",records_no_overdue


        workbook.close()
        f = open(fname.name, "r")
        data = f.read()
        f.close()

        date = fields.Date.context_today(self)
        datas_fname = report_name+" ("+str(date)+").xlsx" # Nombre del Archivo
        
        self.write({'cadena_decoding':"",
            'datas_fname':datas_fname,
            'file':base64.encodestring(data),
            'download_file': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'argil.invoice.analysis.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            }
