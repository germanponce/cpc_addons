# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class IrMailServer(models.Model):
    _inherit = "ir.mail_server"
    
    sender_cmpt = fields.Boolean('Use sender forwarding', help='Sender compliant headers and SMTP envelope information')
    
    @api.model
    def _get_default_bounce_address(self):
        # Si es registro único
        if len(self.ids)==1:
            # Si tiene el ajuste
            if self.sender_cmpt:
                # Si está definido en archivo de configuración o por argumento de línea de comandos, de otro modo del registro
                smtp_user = tools.config.get('smtp_user') or self.smtp_user
        # Caso para conjunto de registros
        else:
            # Se ubica el prioritario del conjunto
            mail_server = mail_server = self.sudo().search([], order='sequence', limit=1)
            # Si se encontró el registro prioritario y tiene el ajuste, tomar el usuario almacenado o de línea de comandos
            if mail_server and mail_server.sender_cmpt:
                return mail_server.smtp_user or tools.config.get('smtp_user')
        # Caso cuando es conjunto de registros sin ajuste o negativo el ajuste unitario
        return super(IrMailServer, self)._get_default_bounce_address()
    
    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False):
        #Contenedor
        mail_server = None
        if mail_server_id:
            # Si viene como parámetro
            mail_server = self.sudo().browse(mail_server_id)
        elif not smtp_server:
            # Si no está como parámetro, se obtiene el prioritario del conjunto
            mail_server = self.sudo().search([], order='sequence', limit=1)
        # Si el registro encontrado tiene activada tal opción
        if mail_server and mail_server.sender_cmpt:
            #Tomar el usuario almacenado o de línea de comandos y añadir la cabecera
            smtp_user = mail_server.smtp_user or tools.config.get('smtp_user') or smtp_user
            message['Sender']=smtp_user
            
        return super(IrMailServer, self).send_email(message, mail_server_id, smtp_server, smtp_port, smtp_user, smtp_password, smtp_encryption, smtp_debug)
