from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    def _create_account_move(
        self,
        balancing_account=False,
        amount_to_balance=0,
        bank_payment_method_diffs=None,
    ):
        res = super()._create_account_move(
            balancing_account, amount_to_balance, bank_payment_method_diffs
        )
        if self.config_id.journal_id.type == "sale":
            if not self.company_id.pos_partner_id:
                return {
                    "type": "ir.actions.act_window",
                    "name": _("Set Default PoS Customer"),
                    "res_model": "res.config.settings",
                    "view_mode": "form",
                    "target": "current",
                    "context": {
                        "res_id": self.env.ref(
                            "point_of_sale.res_config_settings_view_form"
                        ).id
                    },
                }
            self.move_id.write(
                {
                    "partner_id": self.company_id.pos_partner_id.id,
                    "move_type": "out_invoice",
                }
            )
        return res

    def _get_sale_vals(self, key, sale_vals):
        res = super()._get_sale_vals(key, sale_vals)
        if res.get("product_id"):
            res["price_unit"] = abs(sale_vals["amount"]) / sale_vals["quantity"]
        return res
