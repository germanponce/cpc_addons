# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class IrMailServer(models.Model):
    _inherit = "ir.mail_server"
    
    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False):
        
        #VSGTN
        print "\n\n===\nDel módulo mail_server_test:"
        print "message: ", message
        print "mail_server_id: ", mail_server_id
        print "smtp_server: ", smtp_server
        print "smtp_user: ", smtp_user
        print "smtp_password: ", smtp_password
        print "smtp_encryption: ", smtp_encryption
        print "smtp_debug: ", smtp_debug
        print "===\n"
        super(IrMailServer, self).send_email(message, mail_server_id, smtp_server, smtp_port, smtp_user, smtp_password, smtp_encryption, smtp_debug)
