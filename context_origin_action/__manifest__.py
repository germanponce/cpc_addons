# -*- coding: utf-8 -*-

{
    'name': 'Load actions with origin action context',
    'version': '1.0',
    "author": "Argil Consulting",
    "website": "http://www.argil.mx",
    'description': """
This module allows to add a context key 'origin_action' in server action's run RPC call if originating action context include 'context_origin_action' key. This key may use to distinguish originating action from a set of them for same model.
""",
    'depends': ['web',],
    'installable': True,
}
