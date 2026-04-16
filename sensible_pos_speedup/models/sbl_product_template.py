# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SBLProductTemplate(models.Model):
    _inherit = 'product.template'

    sbl_always_load_in_pos = fields.Boolean(
        string="Always Load in POS",
        default=False,
        help="Force this product to be loaded immediately in POS, regardless of the configured product limit. "
             "Use this for critical products like daily specials, popular items, or promotional products."
    )

    @api.onchange('available_in_pos')
    def _onchange_available_in_pos_sbl(self):
        """Reset always load flag when product is removed from POS"""
        if not self.available_in_pos:
            self.sbl_always_load_in_pos = False

    @api.constrains('sbl_always_load_in_pos', 'available_in_pos')
    def _check_sbl_always_load_consistency(self):
        """Ensure always load products are also available in POS"""
        for template in self:
            if template.sbl_always_load_in_pos and not template.available_in_pos:
                raise ValidationError(_("Product '%s' cannot be marked as 'Always Load in POS' "
                                      "if it's not available in POS.") % template.name)