# -*- encoding: utf-8 -*-

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
from openerp import release
if release.major_version in ("9.0", "10.0"):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
#elif release.major_version == "11.0":
#    import importlib
#    importlib.reload(sys)
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from lxml import etree as et
from suds.client import Client
import xmltodict
import base64
from xml.dom.minidom import parse, parseString
import MySQLdb

class invoice_fit(models.Model):
    _inherit = 'account.invoice'

    validate_attachment_bobeda = fields.Boolean(string='Sin Validar en Bobeda Fiscal', track_visibility='onchange',
                                         help='Active esta casilla cuando quiera validar una factura cuyo CFDI no se encuentre vigente en el SAT')
    
    fiscal_uuid = fields.Char('UUID Fiscal', size=128, copy=False, track_visibility="onchange", readonly=True)

    bobeda_consult_amount = fields.Float('Monto Factura de Bobeda')


    @api.multi
    def invoice_validate(self):
        result =  super(invoice_fit, self).invoice_validate()

        for rec in self:
            if rec.type in ('in_invoice','in_refund'):
                if rec.validate_attachment_bobeda == False:                
                    if not rec.fiscal_uuid:
                        raise UserError(_('La factura no contiene un UUID Fiscal, consulte la Bobeda Fiscal (CFDI)'))
                    rec.message_post(body=_("La factura (XML) adjunta se encuentra Vigente en la Bobeda Fiscal\n%s") % (rec.fiscal_uuid))
        return result



    @api.constrains('fiscal_uuid')
    def _constraint_fiscal_uuid(self):
        if self.fiscal_uuid:
            other_ids = self.search([('id','!=',self.id),('fiscal_uuid','=',self.fiscal_uuid)])
            if other_ids:
                raise ValidationError(_('Error !\nEl UUID Fiscal debe ser Unico en el registro de Facturas.\nFactura que contiene el UUID: %s' % other_ids[0].number))
        return True
    

class BobedaMySQL(models.Model):
    _name = 'bobeda.my.sql'
    _description = 'configuracion de la Base de Datos para Bobeda Fiscal'
    _rec_name = 'user' 

    user = fields.Char('Usuario', size=128, required=True)
    password = fields.Char('Password', size=128, required=True)
    host = fields.Char('Direccion Host B.D.', size=128, required=True)
    db = fields.Char('Base de Datos', size=128, required=True)
    port = fields.Integer('Puerto', required=True, default=3306)

    @api.constrains('user')
    def _constraint_parameter_bobeda(self):
        if self.user:
            other_ids = self.search([('id','!=',self.id)])
            if other_ids:
                raise ValidationError(_('Error !\nSolo puede existir una configuración para Bobeda Fiscal.'))
        return True

    @api.constrains('host')
    def _constraint_parameter_bobeda_host(self):
        if self.host:
            if 'http' in self.host:
                raise ValidationError(_('Error !\nEl Host Solo debe contener la Direccion IP sin el HTTP'))
            if ':' in self.host:
                raise ValidationError(_('Error !\nEl Host Solo debe contener la Direccion IP sin :'))
            if '/' in self.host:
                raise ValidationError(_('Error !\nEl Host Solo debe contener la Direccion IP sin /'))
        return True

# import mysql.connector

# cnx = mysql.connector.connect(user='scott', password='password',
#                               host='127.0.0.1',
#                               database='employees')
# cnx.close()


class ConsultBobedaRFC(models.TransientModel):
    _name = 'consult.bobeda.fiscal'
    _description = 'Consultar Bobeda Fiscal'

    bobeda_lines  = fields.One2many('consult.bobeda.fiscal.line','wiz_id','UUID para Seleccion')

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin', default=fields.Date.today())
    serie = fields.Char('Serie', size=64)
    folio = fields.Char('Folio', size=64)

    filter_type =  fields.Selection([
                                        ('periodo','Periodo'),
                                        ('folio_serie','Serie y Folio'),

                                        ], 'Tipo de Busqueda', required=True)

    search_selected = fields.Boolean('Busqueda Seleccionada', default=False)

    invoice_id  = fields.Many2one('account.invoice', 'Factura')

    @api.multi
    def search_uuids(self):
        active_ids = self._context['active_ids']
        bobeda_parameter_obj = self.env['bobeda.my.sql']
        bobeda_id = bobeda_parameter_obj.search([], limit=1)
        if not bobeda_id:
            raise ValidationError("Error!\nNo existen Parametros para la Conexion de Base de Datos con Bobeda Fiscal.")
        user = bobeda_id.user
        password = bobeda_id.password
        host = bobeda_id.host
        db = bobeda_id.db
        port = bobeda_id.port
        # print "#### user >>>>> ",user
        # print "#### password >>>>> ",password
        # print "#### host >>>>> ",host
        # print "#### db >>>>> ",db
        # print "#### port >>>>> ",port
        for rec in self:
            bobeda_lines = []
            for invoice in self.env['account.invoice'].browse(active_ids):
                rfc_emisor = invoice.partner_id.vat
                if not rfc_emisor:
                    raise UserError("Error!\nEl proveedor no tiene un RFC.")
                if rfc_emisor[0:2]=='MX' and len(rfc_emisor) > 12:
                    rfc_emisor  = rfc_emisor[2:]
                    # print "######### RFC EMISOR >> ",rfc_emisor
                rfc_receptor = invoice.company_id.partner_id.vat
                if not rfc_receptor:
                    raise UserError("Error!\nLa Compañia no tiene un RFC.")
                if rfc_receptor[0:2]=='MX' and len(rfc_receptor) > 12:
                    rfc_receptor  = rfc_receptor[2:]

                # print "#### RFC RECEPTOR >>>  ",rfc_receptor
            db = MySQLdb.connect(host=host, user=user,passwd=password, db=db)
            # print "###### db >>>> ",db

            cursor = db.cursor()
            # print "### CURSOR >>>> ",cursor
            if rec.filter_type == 'folio_serie':
                if not rec.serie and not rec.folio:
                    raise UserError("Error!\nDebes ingresar al menos un valor para la busqueda de Folios Fiscales.")
                cr_res = ()
                if rec.serie and rec.folio:
                    cursor.execute("""select UPPER(uuid), 
                                             UPPER(serie),
                                             UPPER(folio),
                                             fechaBusqueda,
                                             total
                                      from cfd_recibido
                                        where UPPER(mi_rfc) = %s
                                          and UPPER(rfc) = %s
                                          and UPPER(serie) = %s
                                          and UPPER(folio) = %s
                        """,(rfc_receptor.upper(),rfc_emisor.upper(),rec.serie.upper(),rec.folio.upper()))
                    cr_res = cursor.fetchall()
                    # print "########### CR_RES >>>>>> ",cr_res
                if rec.serie and not rec.folio:
                    cursor.execute("""select UPPER(uuid), 
                                             UPPER(serie),
                                             UPPER(folio),
                                             fechaBusqueda,
                                             total
                                      from cfd_recibido
                                        where UPPER(mi_rfc) = %s
                                          and UPPER(rfc) = %s
                                          and UPPER(serie) = %s
                        """,(rfc_receptor.upper(),rfc_emisor.upper(),rec.serie.upper()))
                    cr_res = cursor.fetchall()
                    # print "########### CR_RES >>>>>> ",cr_res
                if rec.folio and not rec.serie:
                    cursor.execute("""select UPPER(uuid), 
                                             UPPER(serie),
                                             UPPER(folio),
                                             fechaBusqueda,
                                             total
                                      from cfd_recibido
                                        where UPPER(mi_rfc) = %s
                                          and UPPER(rfc) = %s
                                          and UPPER(folio) = %s
                        """,(rfc_receptor.upper(),rfc_emisor.upper(),rec.folio.upper()))
                    cr_res = cursor.fetchall()
                    # print "########### CR_RES >>>>>> ",cr_res
                if not cr_res or not cr_res[0]:
                    raise UserError("Error!\nNo se encontraron resultados, intente nuevamente.")
                if cr_res:
                    for x in cr_res:
                        try:
                            fiscal_uuid = x[0]
                        except:
                            fiscal_uuid = ''
                        try:
                            serie = x[1]
                        except:
                            serie = ''
                        try:
                            folio = x[2]
                        except:
                            folio = ''
                        try:
                            date = x[3]
                        except:
                            date = ''
                        try:
                            amount_invoice = x[4]
                        except:
                            amount_invoice = 0.0
                        # print "########## fiscal_uuid >>> ",fiscal_uuid
                        # print "########## serie >>> ",serie
                        # print "########## folio >>> ",folio
                        # print "########## date >>> ",date
                        # print "########## amount_invoice >>> ",amount_invoice
                        bobeda_lines.append((0,0,{
                            'fiscal_uuid': fiscal_uuid,
                            'serie': serie,
                            'folio': folio,
                            'date': date,
                            'amount_invoice': amount_invoice,

                            }))
                    # print "#### bobeda_lines >>>> ",bobeda_lines
            else:
                cr_res = ()
                cursor.execute("""select UPPER(uuid), 
                                         UPPER(serie),
                                         UPPER(folio),
                                         fechaBusqueda,
                                         total
                                  from cfd_recibido
                                    where UPPER(mi_rfc) = %s
                                      and UPPER(rfc) = %s
                                      and fechaBusqueda between %s and %s
                    """,(rfc_receptor.upper(),rfc_emisor.upper(), rec.date_start, rec.date_end))
                cr_res = cursor.fetchall()
                # print "########### CR_RES >>>>>> ",cr_res
                # and STR_TO_DATE(fechaBusqueda, '%Y-%m-%d') between %s and %s

                if not cr_res or not cr_res[0]:
                    raise UserError("Error!\nNo se encontraron resultados, intente nuevamente.")
                if cr_res:
                    for x in cr_res:
                        try:
                            fiscal_uuid = x[0]
                        except:
                            fiscal_uuid = ''
                        try:
                            serie = x[1]
                        except:
                            serie = ''
                        try:
                            folio = x[2]
                        except:
                            folio = ''
                        try:
                            date = x[3]
                        except:
                            date = ''
                        try:
                            amount_invoice = x[4]
                        except:
                            amount_invoice = 0.0

                        bobeda_lines.append((0,0,{
                            'fiscal_uuid': fiscal_uuid,
                            'serie': serie,
                            'folio': folio,
                            'date': date,
                            'amount_invoice': amount_invoice,

                            }))

            if not bobeda_lines:
                raise UserError("Error!\nNo se encontraron resultados, intente nuevamente.")

            # cursor.execute("""select mi_rfc,serie,folio,rfc as rfc_proveedor,uuid,FechaTimbrado,fecha_add,estado_cfdi_fecha,
            #                     fechaBusqueda,STR_TO_DATE(fechaBusqueda, '%Y-%m-%d') AS fechaBusquedaTimeConvert from cfd_recibido order by fechaBusqueda desc limit 1;""")

            # cr_res = cursor.fetchall()

            # print "######## RESULTADO >>>>>>>>> ",cr_res

            rec.write({'search_selected': True,
                        'bobeda_lines': bobeda_lines,
                        'invoice_id': active_ids[0]
                        })
            db.close()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'consult.bobeda.fiscal',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': rec.id,
                'views': [(False, 'form')],
                'target': 'new',
                }

    @api.multi
    def insert_uuid(self):
        active_ids = self._context['active_ids']
        # print "########## UUID >>> ",active_ids
        for rec in self:
            count=0
            fiscal_uuid  = ""
            for line in rec.bobeda_lines:
                if line.insert:
                    count+=1
                    fiscal_uuid = line.fiscal_uuid
                    bobeda_consult_amount = line.amount_invoice
                    # print "### fiscal_uuid >>> ",fiscal_uuid
                    # print "### bobeda_consult_amount >>> ",bobeda_consult_amount

            
            if count > 1:
                raise ValidationError('Error!\nSolo puedes insertar un UUID.')
            if count == 0:
                raise ValidationError('Error!\nDebes seleccionar un UUID a insertar.')

            parameter = float(self.env['ir.config_parameter'].get_param('bobeda_tolerance_range_between_invoice_record_and_cfdi_xml_file')) or 0
            low = bobeda_consult_amount - parameter
            upp = bobeda_consult_amount + parameter
            if not low < rec.invoice_id.amount_total < upp:
                raise UserError(_('Inconsistencia de datos\n\nEl total del CFDI de Boveda (%f) supera al registro en Odoo o se encuentra fuera del rango de tolerancia de +/- %f') % (bobeda_consult_amount, parameter))

            rec.bobeda_lines.unlink()
            rec.invoice_id.write({
                                    'fiscal_uuid': fiscal_uuid,
                                    'bobeda_consult_amount': bobeda_consult_amount,
                                })
        return True
        # self.write({'cadena_decoding':"",
        #     'datas_fname':datas_fname,
        #     'file':base64.encodestring(data),
        #     'download_file': True})
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'cash.flow.report.wizard',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'res_id': self.id,
        #     'views': [(False, 'form')],
        #     'target': 'new',
        #     }


    @api.constrains('date_start','date_end')
    def _constraint_period(self):
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise ValidationError(_('Error !\nEl Periodo esta mal establecido.'))
        return True

class ConsultBobedaRFCLine(models.TransientModel):
    _name = 'consult.bobeda.fiscal.line'
    _description = 'Consultar Bobeda Fiscal Linea Insercion'
    _order = 'date desc'

    fiscal_uuid = fields.Char('UUID Fiscal')
    serie = fields.Char('Serie')
    folio = fields.Char('Folio')
    date = fields.Date('Fecha Factura')
    amount_invoice = fields.Float('Monto Factura')
    insert = fields.Boolean('Insertar UUID')
    wiz_id = fields.Many2one('consult.bobeda.fiscal','ID Ref')