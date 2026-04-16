/** @odoo-module **/
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { PromotionCodePopup } from "./promotion_code_popup";
import { _t } from "@web/core/l10n/translation";

export async function redeemCampaign(env, order, lealCustomerUid, acumlationData) {
    // const orderlines = order.get_orderlines();
    const leal_campaign_redeem_data = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : [];

    for (const redeem_data of leal_campaign_redeem_data) {
        const commerce = await env.services.pos.data.call(
            "leal.user.data",
            "search_read",
            [[['activo', '=', true]]],
            { fields: ['uid_cms', 'id_comercio', 'nombre_comercio', 'id_sucursal', 'tiene_otp'], limit: 1 }
        )
        if (redeem_data !== null && ("is_campaign_reward" in redeem_data) && redeem_data.is_campaign_reward) {
            // Obtener configuración de hidden_characters
            let hiddenCharacters = 4;
            try {
                const config = await env.services.pos.data.call(
                    "leal.api.settings",
                    "search_read",
                    [[['active', '=', true]]],
                    { fields: ['hidden_characters'], limit: 1 }
                );
                hiddenCharacters = config[0].hidden_characters || 4;
            } catch (error) {
                console.warn("No se pudo cargar la configuración de hidden_characters, usando valor por defecto:", error);
            }

            env.services.ui.unblock();
            const promoResult = await makeAwaitable(env.services.dialog, PromotionCodePopup, {
                title: _t("Código de Promoción"),
                body: _t("Confirme el código de promoción para continuar"),
                hiddenCharacters: hiddenCharacters
            });

            const confirmed = promoResult?.confirmed ?? false;
            const promotionCode = promoResult?.promotionCode ?? null;

            if (confirmed && promotionCode) {
                env.services.ui.block();
                const lastDigitsOriginal = redeem_data.promotion_code.slice(-hiddenCharacters);
                if (String(promotionCode).toLowerCase() === lastDigitsOriginal.toLowerCase()) {
                    //Acumulación de puntos
                    const resultAccumulation = await env.services.pos.data.call(
                        "leal.api.settings",
                        "leal_accumulation",
                        [acumlationData],
                        {}
                    );

                    if (resultAccumulation.message !== null && resultAccumulation.code != 100) {
                        env.services.ui.unblock();
                        env.services.notification.add(
                            "Error al acumular puntos Leal: " + resultAccumulation.message,
                            { type: 'danger', sticky: true, }
                        );
                        return false;
                    }
                    const transactionId = resultAccumulation.id_transaccion || null;
                    if (!transactionId) {
                        env.services.ui.unblock();
                        console.error("No se recibió ID de transacción para la redención de campaña.");
                        return false;
                    }
                    let redeem = {
                        "code": redeem_data.promotion_code,
                        "transaction_id": transactionId,
                        "campaign_id": redeem_data.campaign_id,
                        "uid": lealCustomerUid,
                        "uid_cms": commerce[0].uid_cms,
                        "invoice_number": order.name,
                        "benefit_amount": redeem_data.benefit_amount,
                        "note": ""
                    }
                    const result = await env.services.pos.data.call(
                        "leal.api.settings",
                        "leal_campaign_redeem",
                        [redeem],
                        {}
                    );
                    if (result.status === 'success') {
                        env.services.ui.unblock();
                        env.services.notification.add(
                            _t(`Redención exitosa: ${result.message}`),
                            { type: "success" }
                        );
                        //Borrado de data de redención
                        localStorage.removeItem('leal_campaign_redeem_data');
                        try {
                            await env.services.pos.data.call(
                                "leal.customer.campaign",
                                "delete_customer_campaigns",
                                [lealCustomerUid, env.services.pos.config.id],
                                {}
                            );
                        } catch (error) {
                            console.error("Error al guardar campañas del cliente después de la redención:", error);
                        }

                        return true;
                    } else {
                        env.services.ui.unblock();
                        env.services.notification.add(
                            _t(`Error haciendo redención de campañas. ${result.message}`),
                            { type: "danger" }
                        );
                        return false;
                    }

                }
                else {
                    env.services.ui.unblock();
                    env.services.notification.add(
                        _t(`Los últimos ${hiddenCharacters} dígitos ingresados no coinciden con el código de promoción.`),
                        { type: "danger" }
                    );
                    return false;
                }

            }
            else {
                console.warn('Redención cancelada por el usuario');
                return false;
            }

        }
    }

    return true;
}