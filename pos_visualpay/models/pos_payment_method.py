from odoo import api, fields, models, _

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'
    
    def _get_payment_method_type(self):
        selection = [
            ('none', 'None required'),
            ('terminal', 'Terminal'),
            ('visualpay', 'Visual Pay')
        ]
        if self.env['res.partner.bank'].get_available_qr_methods_in_sequence():
            selection.append(('qr_code', 'Bank App (QR Code)'))
        return selection

    visualpay_image = fields.Image(
        string="VisualPay Image",
        help="Upload an image or QR code used for VisualPay integration.",
        max_width=1000, max_height=1000
    )

    visualpay_description = fields.Text(
        string="VisualPay Description",
        help="Enter a description or instructions for this VisualPay method."
    )

    visualpay_require_confirmation = fields.Boolean(
        string="Require Payment Confirmation",
        help="Enable this option if the customer must upload a proof of payment (e.g. receipt image) before confirming the order."
    )
    payment_method_type = fields.Selection(selection=_get_payment_method_type, string="Integration", default='none', required=True)
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)

        extra_fields = [
            'visualpay_image',
            'visualpay_description',
            'visualpay_require_confirmation'
        ]
        for f in extra_fields:
            if f not in fields_list:
                fields_list.append(f)
        return fields_list