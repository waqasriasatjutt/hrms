from odoo import models, fields

class POSConfig(models.Model):
    _inherit = "pos.config"

    screensaver_logo = fields.Binary(
        string="Screensaver Logo",
        attachment=True,
        help="Upload a custom POS screensaver logo."
    )
    pos_navbar_logo = fields.Binary(
        string="Navbar Logo",
        attachment=True,
        help="Upload a custom POS navbar logo."
    )
    pos_theme_color = fields.Char(
        string="POS Header Color",
        default="#004d99",
        help="Custom color for the POS navbar/header."
    )
    screensaver_timeout = fields.Integer(
        string="Idle Timeout (seconds)",
        default=60,
        help="Time of inactivity (in seconds) before showing the POS screensaver."
    )
