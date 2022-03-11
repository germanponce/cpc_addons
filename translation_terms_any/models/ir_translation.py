# -*- encoding: utf-8 -*-

from openerp import api, models

class IrTranslation(models.Model):
    _inherit = 'ir.translation'
    
    @api.model
    def _get_import_cursor(self):
        """Allow translation updates."""
        return super(IrTranslation, self.with_context(overwrite=True))._get_import_cursor()