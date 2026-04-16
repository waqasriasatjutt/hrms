from odoo import models, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)
_logger.warning("  payment_link_wizard.py LOADED")

class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'amount' in res and 'amount_max' in res:
            res['amount'] = res['amount_max']
        return res

    def _is_payrillium_configured(self):
        """Check if Payrillium is configured and ready to use"""
        config = self.env['payrillium.config'].sudo().search([], limit=1)
        return bool(config and config.installed and config.token)

    @api.depends('amount', 'currency_id', 'partner_id', 'company_id')
    def _compute_link(self):
        """Override to use Payrillium if configured, otherwise use standard Odoo flow"""
        # First, collect records that should use Payrillium vs standard
        payrillium_records = self.browse()
        standard_records = self.browse()
        
        is_payrillium_configured = self._is_payrillium_configured()
        for payment_link in self:
            # Check if Payrillium is configured and this is an invoice
            if payment_link.res_model == 'account.move' and is_payrillium_configured:
                payrillium_records |= payment_link
            else:
                standard_records |= payment_link
        
        # Process Payrillium records
        for payment_link in payrillium_records:
            try:
                # Use Payrillium payment link generation
                from ..services.mirillium.api import create_payment_link
                record = self.env[payment_link.res_model].browse(payment_link.res_id)
                if not record.exists():
                    payment_link.link = ''
                    continue
                
                # Generate Payrillium link
                link_url = create_payment_link(record, amount=payment_link.amount)
                if link_url and isinstance(link_url, str):
                    payment_link.link = link_url
                else:
                    # Fallback to standard if Payrillium fails
                    _logger.warning("Payrillium link generation failed, falling back to standard")
                    # Use standard computation for this record
                    from werkzeug import urls
                    related_document = self.env[payment_link.res_model].browse(payment_link.res_id)
                    base_url = related_document.get_base_url()
                    url = payment_link._prepare_url(base_url, related_document)
                    query_params = payment_link._prepare_query_params(related_document)
                    anchor = payment_link._prepare_anchor()
                    if '?' in url:
                        payment_link.link = f'{url}&{urls.url_encode(query_params)}{anchor}'
                    else:
                        payment_link.link = f'{url}?{urls.url_encode(query_params)}{anchor}'
            except Exception as e:
                _logger.error("Error generating Payrillium link: %s", str(e))
                # Fallback to standard Odoo flow on error
                from werkzeug import urls
                related_document = self.env[payment_link.res_model].browse(payment_link.res_id)
                base_url = related_document.get_base_url()
                url = payment_link._prepare_url(base_url, related_document)
                query_params = payment_link._prepare_query_params(related_document)
                anchor = payment_link._prepare_anchor()
                if '?' in url:
                    payment_link.link = f'{url}&{urls.url_encode(query_params)}{anchor}'
                else:
                    payment_link.link = f'{url}?{urls.url_encode(query_params)}{anchor}'
        
        # Process standard records using parent method
        if standard_records:
            super(PaymentLinkWizard, standard_records)._compute_link()