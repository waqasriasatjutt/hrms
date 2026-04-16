# -*- coding: utf-8 -*-

from odoo import fields, models, api


class IrCron(models.Model):
    _inherit = 'ir.cron'

    def validate_smart_dojo_key(self):
        """Public method to be called by cron job."""
        self.env['res.config.settings'].sudo()._validate_smart_dojo_key()

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        """Hide Smart Dojo cron from UI unless explicitly requested."""
        result = super().search_read(domain, fields, offset, limit, order, **read_kwargs)

        # Only hide if not explicitly allowing smart cron fetch
        if not self.env.context.get('allow_smart_cron_fetch'):
            # Filter out Smart Dojo validation cron from results
            filtered_result = []
            for record in result:
                code = record.get('code', '')
                # Check if this is the Smart Dojo validation cron
                if not (code and 'model._validate_smart_dojo_key()' in code):
                    filtered_result.append(record)
            return filtered_result

        return result
