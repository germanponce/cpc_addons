# -*- encoding: utf-8 -*-

{
    "name"      : "Sender compliance header for Mail server",
    "version"   : "1.0",
    "category"  : "",
    "author"    : "Argil Consulting",
    "website"   : "http://www.argil.mx",
    "depends"   : ["base",],
    "description": """
This module adds sender compliance header for Microsoft SMTP server on eMail Forwarding accounts.
""",
    "data" : [
        'views/ir_mail_server_view.xml',
    ],
    'installable': True
}
