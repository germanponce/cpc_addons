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

class invoice_fit(models.Model):
    _inherit = 'account.invoice'

    foreign_invoice      = fields.Char(string='No. factura extranjera', size=36, readonly=True, states={'draft': [('readonly', False)]})
    validate_attachment  = fields.Boolean(string='Validar sin XML', track_visibility='onchange',
                                         help='Active esta casilla cuando quiera validar una factura sin haber adjuntado el archivo XML del CFDI')
    validate_attachment2 = fields.Boolean(string='Sin Validar en SAT', track_visibility='onchange',
                                         help='Active esta casilla cuando quiera validar una factura cuyo CFDI no se encuentre vigente en el SAT')

    def onchange_attached(self, attachment=False, currency_id=False):
        if attachment:
            xml_data = base64.b64decode(attachment).replace('http://www.sat.gob.mx/cfd/3 ','').replace('Rfc=','rfc=').replace('Fecha=','fecha=').replace('Total=','total=').replace('Folio=','folio=').replace('Serie=','serie=')
            try:
                xmlTree = et.ElementTree(et.fromstring(xml_data))
            except:
                raise UserError(_('Formato de archivo incorrecto 111\n\nSe necesita cargar un archivo de extensión ".xml" (CFDI)'))
            if 'cfdi:Comprobante' not in xml_data[0:100] and 'Comprobante' not in xml_data[0:100]:
                raise UserError(_('Archivo XML incorrecto\n\nSe necesita cargar un archivo de tipo CFDI'))
            else:
                vals = {}
                #if 'cfdi:Comprobante' in xml_data[0:100]:
                vouchNode = xmlTree.getroot()
                if vouchNode is None:
                    raise UserError(_('Estructura CFDI inválida\n\nNo se encontró el nodo "cfdi:Comprobante"'))
                if 'total' not in vouchNode.attrib.keys() or 'fecha' not in vouchNode.attrib.keys():
                    raise UserError(_('Información faltante\n\nCompruebe que el CFDI tenga asignados los campos "total" y "fecha".'))
                emitterNode = vouchNode.find('{http://www.sat.gob.mx/cfd/3}Emisor')
                if emitterNode is None:
                    raise UserError(_('Estructura CFDI inválida\n\nNo se encontró el nodo "cfdi:Emisor"'))
                if 'rfc' not in emitterNode.attrib.keys():
                    raise UserError(_('Información faltante\n\nNo se encontró el RFC emisor.'))
                receiverNode = vouchNode.find('{http://www.sat.gob.mx/cfd/3}Receptor')
                if receiverNode is None:
                    raise UserError(_('Estructura CFDI inválida\n\nNo se encontró el nodo "cfdi:Receptor"'))
                if 'rfc' not in receiverNode.attrib.keys():
                    raise UserError(_('Información faltante\n\nNo se encontró el RFC receptor.'))
                complNode = vouchNode.find('{http://www.sat.gob.mx/cfd/3}Complemento')
                if complNode is None:
                    raise UserError(_('Estructura CFDI inválida\n\nNo se encontró el nodo "cfdi:Complemento"'))
                stampNode = complNode.find('{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital')
                if stampNode is None:
                    raise UserError(_('Estructura CFDI inválida\n\nNo se encontró el nodo "tfd:TimbreFiscalDigital"'))
                if 'UUID' not in stampNode.attrib.keys():
                    raise UserError(_('Información faltante\n\nNo se encontró el Folio Fiscal (UUID)'))
                if len(stampNode.attrib['UUID']) != 36:
                    raise UserError(_('Información incorrecta\n\nEl Folio Fiscal (UUID) %s es incorrecto: se esperaban 36 caracteres, se encontraron %s' % (stampNode.attrib['UUID'], len(stampNode.attrib['UUID']))))
                vals['uuid'] = stampNode.attrib['UUID'].upper()
            vals['compl_currency_id'] = currency_id and currency_id.id or self.env.user.company_id.currency_id.id
            if 'TipoCambio' in vouchNode.attrib.keys():
                try:
                    vals['exchange_rate'] = float(vouchNode.attrib['TipoCambio'] )
                except:
                    vals['exchange_rate'] = 1
            vals['cbb_series'] = vouchNode.attrib.get('serie', '')
            try:
                vals['cbb_number'] = int(vouchNode.attrib.get('folio', 0))
            except:
                pass
            vals.update({
                'rfc': emitterNode.attrib['rfc'],
                'rfc2': receiverNode.attrib['rfc'],
                'compl_date' : vouchNode.attrib['fecha'][0:10],
                'amount' : float(vouchNode.attrib['total']),
            })
            return {'value':vals}
        return {'value':False}

    @api.multi
    def action_move_create(self):
        ### Codigo para validar si es Ingreso Credito o de Contado
        
        # for invoice in self:
        #     if not invoice.amount_total:
        #         continue
        #     payment_term_obj = self.env['account.payment.term']
        #     inv_line_obj = self.env['account.invoice.line']
        #     if invoice.type == 'out_invoice':
        #         for line in invoice.invoice_line_ids:
        #             # Validacion para contabilizar Ingreso a Credito o Contado (segun tenga configurada la cuenta la categoria del producto y/o el producto)
        #             if line.product_id and line.account_id.id in (line.product_id.property_account_income_id.id, line.product_id.property_account_income_id2.id,line.product_id.categ_id.property_account_income_categ_id.id,line.product_id.categ_id.property_account_income_categ_id2.id):
        #                 new_account = bool(invoice.date_invoice == invoice.date_due) and \
        #                                   (line.product_id.property_account_income_id2.id or line.product_id.categ_id.property_account_income_categ_id2.id) or \
        #                                   (line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id)
        #                 if new_account and line.account_id.id != new_account:
        #                     line.write({'account_id': new_account})
        #             ### Fin de Codigo para validar si es Ingreso Credito o de Contado
        
        # Continuación código original
        result = super(invoice_fit, self).action_move_create()
        company = self.env.user.company_id
        for inv in self:
            xpartner = inv.partner_id.parent_id or inv.partner_id
            attachment = self.env['ir.attachment'].search([('name', 'ilike', '.xml'), ('res_model', '=', 'account.invoice'), ('res_id', '=', inv.id)], limit=1)
            if attachment:
                user = self.env.user
                cmpl_vals = inv.onchange_attached(attachment=attachment.datas, currency_id=inv.currency_id)['value']
                if not xpartner.vat:
                    raise UserError(_('Información faltante\n\nEl proveedor %s no tiene configurado un R.F.C.') % xpartner.name)
                partner_vat = xpartner.vat[2:] if len(xpartner.vat) > 13 else xpartner.vat
                if partner_vat != cmpl_vals['rfc']:
                    raise UserError(_('Inconsistencia de datos.\n\nEl RFC emisor ("%s") no coincide con el RFC del proveedor ("%s")') % (cmpl_vals['rfc'], partner_vat))
                if not user.company_id.partner_id.vat:
                    raise UserError(_('Inconsistencia de datos\n\nEl RFC receptor ("%s") no existe en la Compañia o no esta asignado.\n "%s"') % (cmpl_vals['rfc2'], user.company_id.name))
                if user.company_id.partner_id.vat[2:] != cmpl_vals['rfc2']:
                    raise UserError(_('Inconsistencia de datos\n\nEl RFC receptor ("%s") no coincide con el RFC de la empresa ("%s")') % (cmpl_vals['rfc2'], user.company_id.vat[2:]))
                parameter = float(self.env['ir.config_parameter'].get_param('argil_tolerance_range_between_invoice_record_and_cfdi_xml_file')) or 0
                low = inv.amount_total - parameter
                upp = inv.amount_total + parameter
                if not low < cmpl_vals['amount'] < upp:
                    raise UserError(_('Inconsistencia de datos\n\nEl total del XML (%f) está fuera del rango de tolerancia de +/- %f') % (cmpl_vals['amount'], parameter))
            # inv.move_id.write({'item_concept': company._assembly_concept(inv.type, invoice=inv)})
        return result
                                

    @api.multi
    def invoice_validate(self):
        result =  super(invoice_fit, self).invoice_validate()

        for rec in self:
            if rec.type in ('in_invoice','in_refund'):
                if rec.validate_attachment == False:
                    attachment_xml_ids = self.env['ir.attachment'].search([('res_model', '=', 'account.invoice'), ('res_id', '=', rec.id), ('name', 'ilike', '.xml')], limit=1)
                    if not attachment_xml_ids:
                        raise UserError(_('No Puede Validar la Factura o Nota de Credito sin el archivo XML del CFDI...'))
                    elif attachment_xml_ids and not rec.validate_attachment2:
                        uuid = False
                        url = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl'
                        try:
                            client = Client(url)
                        except:
                            raise UserError(_('No se pudo establecer la conexión con el sitio del SAT para validar la factura, por favor revise su conexión de internet y/o espere a que el sitio del SAT se encuentre disponible...'))
                        for att in attachment_xml_ids:
                            xml_data = base64.b64decode(att.datas).replace('http://www.sat.gob.mx/cfd/3 ', '').replace('Rfc=','rfc=').replace('Fecha=','fecha=').replace('Total=','total=').replace('Folio=','folio=').replace('Serie=','serie=')
                            result = False
                            try:
                                xmlTree = et.ElementTree(et.fromstring(xml_data))
                                vouchNode = xmlTree.getroot()
                                uuid = vouchNode.find('{http://www.sat.gob.mx/cfd/3}Complemento').find('{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital').attrib['UUID'].upper()
                                rfc_emisor = vouchNode.find('{http://www.sat.gob.mx/cfd/3}Emisor').attrib['rfc'].upper()
                                rfc_receptor = vouchNode.find('{http://www.sat.gob.mx/cfd/3}Receptor').attrib['rfc'].upper()
                                monto_total = float(vouchNode.attrib['total'])
                                result = client.service.Consulta(""""?re=%s&rr=%s&tt=%s&id=%s""" % (rfc_emisor, rfc_receptor, monto_total, uuid))
                            except:
                                continue
                            if result and result.Estado != 'Vigente':
                                raise UserError(
                                        _('No Puede Validar la Factura o Nota de Credito, el SAT devolvió lo siguiente: .\n\n'
                                          'Codigo Estatus: %s\n'
                                          'Estado: %s\n\n'
                                          'Folio Fiscal: %s\n'
                                          'RFC Emisor: %s\n'
                                          'RFC Receptor: %s\n'
                                          'Monto Total: %d') % (result.CodigoEstatus, result.Estado, uuid, rfc_emisor, rfc_receptor, monto_total))
                        if not uuid:
                            raise UserError(_('Formato de archivo XML incorrecto\n\nSe necesita cargar un archivo de extensión ".xml" (CFDI)'))
                    rec.message_post(body=_("La factura (XML) adjunta se encuentra Vigente en el SAT\n%s") % (result))
        return result

invoice_fit()
