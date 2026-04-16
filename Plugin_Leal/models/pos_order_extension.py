# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)

class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    def check(self):
        order_id = self.env.context.get('active_id')
        if order_id:
            order = self.env['pos.order'].browse(order_id)
            if order and order.refunded_order_ids:
                original_order = order.refunded_order_ids[0]

                # Comprobar si la orden original tiene un método de pago 'Leal'
                has_leal_payment = any(p.payment_method_id.name.lower() == 'leal' for p in original_order.payment_ids)

                if has_leal_payment:
                    # Si se pagó con Leal, bloquear la anulación desde el backend
                    raise exceptions.UserError(
                        "Las devoluciones de órdenes pagadas con Leal deben procesarse desde la interfaz del Punto de Venta (POS) para asegurar la correcta anulación de los puntos. Por favor, realice la devolución desde el POS."
                    )
                else:
                    # Si no se pagó con Leal, proceder con la lógica de anulación existente
                    _logger.info(f"Processing refund for POS order {order.pos_reference} (No Leal Payment)")
                    for line in order.lines:
                        if line.qty < 0 and line.refunded_orderline_id:
                            original_line = line.refunded_orderline_id
                            original_order_ticket_code = original_line.order_id.pos_reference
                            product_id = original_line.product_id.id

                            leal_transactions = self.env['leal.redeem.response'].search([
                                ('no_factura', '=', original_order_ticket_code),
                                ('odoo_product_id', '=', product_id),
                                ('state', '=', 'success')
                            ])

                            _logger.info(f"Found {len(leal_transactions)} Leal item redeem transactions for order {original_order_ticket_code} and product {product_id}")

                            for transaction in leal_transactions:
                                refund_data = {
                                    'id_comercio': transaction.id_comercio or "",
                                    'id_sucursal': transaction.id_sucursal or "",
                                    'uid': transaction.uid_customer or "",
                                    'id_transaccion': transaction.id_transaccion or "",
                                    'nota': f'Anulación el {fields.Datetime.now()} hecho por {self.env.user.name}',
                                }
                                try:
                                    self.env['leal.api.settings'].refund_order(refund_data)
                                    _logger.info(f"Successfully refunded Leal transaction {transaction.id_transaccion}")
                                except Exception as e:
                                    _logger.error(f"Failed to refund Leal transaction {transaction.id_transaccion}: {e}")
                                    # Opcional: podrías lanzar un error si la anulación es crítica
                                    # raise exceptions.UserError(f"Failed to refund Leal transaction: {e}")

        res = super(PosMakePayment, self).check()
        return res

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    leal_redeem_data = fields.Json(string="Leal Redeem Data", default={})

    def _get_fields_for_order_line(self):
        fields = super()._get_fields_for_order_line()
        fields.append('leal_redeem_data')
        return fields

    @api.model_create_multi
    def create(self, vals_list):
        # Ensure leal_redeem_data is present for each created line (batch-safe)
        for vals in vals_list:
            if 'leal_redeem_data' not in vals:
                vals['leal_redeem_data'] = {}
        return super(PosOrderLine, self).create(vals_list)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_line_fields(self, line, session_id=None):
        fields_data = super()._order_line_fields(line, session_id)
        # Asegurar que leal_redeem_data esté siempre presente
        if 'leal_redeem_data' not in line[2]:
            fields_data[2]['leal_redeem_data'] = {}
        else:
            fields_data[2]['leal_redeem_data'] = line[2]['leal_redeem_data']
        return fields_data
