/** @odoo-module **/
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { CustomerSearchPopup } from "./customer_search_popup";
import { OTPInputPopup } from "./otp_input_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { LealPointsChoicePopup } from "./leal_points_choice_popup";


export function isRefund(order) {
    const orderlines = order.get_orderlines();
    const isRefund = orderlines.some(line => line.refunded_orderline_id);
    return isRefund;
}

export async function refundAction(order, env, pos) {
    const orderlines = order.get_orderlines();
    for (const orderline of orderlines) {
        if (orderline.refunded_orderline_id) {
            const originalOrderPayments = await pos.data.call(
                "leal.redeem.response",
                "get_order_from_orderline_id",
                [orderline.refunded_orderline_id.id]
            );

            const originalLealPayment = originalOrderPayments.find(p => p.name.toLowerCase() === 'leal');

            if (originalLealPayment) {
                const lealAmount = originalLealPayment.amount;
                const currentPaymentLines = order.payment_ids;
                const currentLealPaymentLine = currentPaymentLines.find(pl => pl.payment_method_id.name.toLowerCase() === 'leal');

                if (!currentLealPaymentLine || Math.abs(currentLealPaymentLine.get_amount()) !== lealAmount) {
                    env.services.ui.unblock();
                    env.services.dialog.add(ConfirmationDialog, {
                        title: _t("Error en Devolución Leal"),
                        body: _t(`La devolución debe incluir el método de pago Leal por el mismo valor que la compra original ($${lealAmount.toFixed(2)}). Por favor, revise los métodos de devolución.`),
                        confirmLabel: _t("Entendido"),
                    });
                    return false;
                }
            }
            break;
        }
    }

    const originalOrderName = await pos.data.call(
        "leal.redeem.response",
        "get_ticket_code_from_orderline_id",
        [orderlines[0].refunded_orderline_id.id],
        {}
    );


    const lealOrder = await pos.data.call(
        "leal.redeem.response",
        "find_order_by_partial_invoice",
        [originalOrderName],
        {}
    );
    const refund_data = {
        id_comercio: lealOrder[0].id_comercio || "",
        id_externo: pos.config.id.toString(),
        uid: lealOrder[0].uid_customer || "",
        id_transaccion: lealOrder[0].id_transaccion || "",
        nota: `Anulación el ${new Date().toISOString()} hecho por ${pos.user.name}`,
    }

    const resp_refund = await pos.data.call(
        "leal.api.settings",
        "refund_order",
        [refund_data],
        {}
    );
    if (resp_refund.code !== 100) {
        env.services.ui.unblock();
        if (resp_refund.message.includes("no ha sido encontrada")) {
            return true;
        }

        env.services.dialog.add(ConfirmationDialog, {
            title: _t("Error al Anular Orden"),
            body: _t(`No se pudo anular la orden en Leal. Error: ${resp_refund.message}`),
            confirmLabel: _t("Entendido"),
        });
        return false;
    }
    else {
        env.services.ui.unblock();
        env.services.notification.add(
            "Puntos Leal anulados correctamente.",
            { type: 'success' }
        );
        return true;
    }
}

// @Deprecated: This function is deprecated and should not be used in new code.
export async function refundActionDiscItem(order, env) {
    const orderlines = order.get_orderlines();
    for (const orderline of orderlines) {
        if (orderline.refunded_orderline_id) {
            try {
                const originalOrderName = await env.services.rpc("/web/dataset/call_kw", {
                    model: "leal.redeem.response",
                    method: "get_ticket_code_from_orderline_id",
                    args: [orderline.refunded_orderline_id],
                    kwargs: {}
                });

                if (originalOrderName) {
                    const lealOrder = await env.services.rpc("/web/dataset/call_kw", {
                        model: "leal.redeem.response",
                        method: "find_order_by_partial_invoice",
                        args: [originalOrderName],
                        kwargs: {}
                    });

                    if (lealOrder && lealOrder.length > 0) {
                        const matchingLealOrder = lealOrder.find((lealRecord) => lealRecord.odoo_product_id && lealRecord.odoo_product_id[0] === orderline.product.id);

                        if (matchingLealOrder) {
                            const refund_data = {
                                id_comercio: matchingLealOrder.id_comercio || "",
                                id_sucursal: matchingLealOrder.id_sucursal || "",
                                uid: matchingLealOrder.uid_customer || "",
                                id_transaccion: matchingLealOrder.id_transaccion || "",
                                nota: `Anulación el ${new Date().toISOString()} hecho por ${env.services.user.name}`,
                            }
                            const resp_refund = await env.services.rpc("/web/dataset/call_kw", {
                                model: "leal.api.settings",
                                method: "refund_order",
                                args: [refund_data],
                                kwargs: {},
                            });
                        }
                    }
                } else {
                    console.warn(`No se pudo obtener el nombre de la orden para la línea ${orderline.refunded_orderline_id}`);
                }

            } catch (error) {
                console.error(`Error al buscar información de la línea ${orderline.refunded_orderline_id}:`, error);
            }
        }
    }
}

export async function validateToken(pos, env) {
    // Verificar que el token está activo
    const tokenResult = await pos.data.call(
        "leal.api.settings",
        "get_token_for_frontend",
        [],
        {}
    );
    if (!tokenResult.success) {
        let title = "Token Inválido";
        let message = `Error: ${tokenResult.message}`;

        if (!tokenResult.config_exists) {
            title = "Configuración Faltante";
            message = "No hay configuración de Leal API.\n\nDebe configurar primero:\n• URL de API\n• Usuario y contraseña";
        } else if (!tokenResult.is_authenticated) {
            title = "🔑 Autenticación Requerida";
            message = "La configuración existe pero no está autenticada.\n\n Por favor autentíquese con sus credenciales.";
        }

        message += "\n\n Vaya a:\nConfiguraciones → Técnico → Leal Redeem";
        env.services.ui.unblock();
        this.dialog.add(ConfirmationDialog, {
            title: _t(title),
            body: _t(message),
            confirmText: _t("Entendido"),
            cancelText: _t("Cerrar")
        });
        return;

    }
    return tokenResult.token;
}

export async function validateCustomer(pos, dialog, env) {
    let customerUID;
    let lealUser;
    const currentOrder = pos.get_order();
    let customerName = null;


    const currentPartner = currentOrder.get_partner();

    if (currentPartner) {
        if (!currentPartner.vat || currentPartner === false) {
            env.services.dialog.add(ConfirmationDialog, {
                title: _t("Documento requerido"),
                body: _t(`El cliente ${currentPartner.name} no tiene documento configurado.\n\nPor favor configure el documento del cliente antes de continuar.`),
                confirmLabel: _t("Entendido"),
            });
            return;
        }
    }


    if (currentPartner && currentPartner.vat) {
        // Cliente ya seleccionado - buscar directamente en Leal con su documento
        const customerSearchResult = await pos.data.call(
            "leal.api.settings",
            "search_customer",
            [currentPartner.vat],
            {}
        );

        if (customerSearchResult.success && customerSearchResult.data && customerSearchResult.data.length > 0) {
            // FIXME: Se deja el último resultado cuando vienen duplicados
            lealUser = customerSearchResult.data[customerSearchResult.data.length - 1];
            customerUID = lealUser.uid;
            customerName = currentPartner.name;
        } else {
            env.services.ui.unblock();
            env.services.dialog.add(ConfirmationDialog, {
                title: _t("Cliente no encontrado en Leal"),
                body: _t(`El cliente ${currentPartner.name} con documento ${currentPartner.vat} no fue encontrado en Leal.`),
                confirmLabel: _t("Entendido"),
            });
            return;
        }
    } else {
        // No hay cliente seleccionado - mostrar popup de búsqueda
        env.services.ui.unblock();
        const payload = await makeAwaitable(dialog, CustomerSearchPopup, {
            title: _t("Buscar Cliente en Leal"),
            confirmText: _t("Buscar"),
            cancelText: _t("Cancelar"),
        });
        if (payload && payload.selectedCustomer) {
            const customerData = payload.selectedCustomer;
            // Validar que el documento existe en Odoo POS
            const odooCustomer = await pos.data.call(
                "res.partner",
                "search_read",
                [[["vat", "=", customerData.cedula]], ['id', 'name', 'vat'], 0, 1]
            );
            if (!odooCustomer || odooCustomer.length === 0) {
                dialog.add(ConfirmationDialog, {
                    title: _t("Cliente no encontrado"),
                    body: _t(`El cliente con documento ${customerData.cedula} no existe en el sistema Odoo.\n\nPor favor registre al cliente antes de continuar.`),
                });
                return;
            }
            const posCustomer = pos.models['res.partner'].find(p => p.id === odooCustomer[0].id);
            if (posCustomer) {
                currentOrder.set_partner(posCustomer);
            }
            lealUser = customerData;
            return lealUser;
        }
        else {
            return;
        }
    }
    return lealUser;
}

export async function calculateAuthValue(env, pos, lealUser) {
    // Calcular el valor de autorización
    const currentOrder = env.services.pos.get_order();
    const totalAmount = currentOrder.get_total_with_tax();


    const valor_por_punto_redencion = await pos.data.call(
        "leal.user.config",
        "search_read",
        [[['config_key', '=', 'valor_por_punto_redencion']], ['config_value_int'], 0, 1]
    );

    const totalAmountLeal = lealUser.puntos_activos * (valor_por_punto_redencion[0].config_value_int);

    // Mostrar popup para redimir puntos
    env.services.ui.unblock();
    const { confirmed, useAll, monto } = await makeAwaitable(env.services.dialog, LealPointsChoicePopup, {
        puntos: lealUser.puntos_activos,
        valorPesos: totalAmountLeal,
        confirmText: _t("Confirmar"),
    });
    if (!confirmed) return;

    // Validar el monto a redimir
    let montoRedimir = monto;
    if (montoRedimir > totalAmount) {
        montoRedimir = totalAmount;
    }
    // Retornar el monto final a redimir
    return montoRedimir;
}

export async function validateIfExistsOTP(env, pos, dialog, lealUser, montoRedimir, paymentMethod) {
    env.services.ui.block();
    const currentOrder = env.services.pos.get_order();
    // Validación si ya se agregó la línea de pago Leal
    for (const p of currentOrder.payment_ids) {
        if (p.payment_method_id && p.payment_method_id.name.toLowerCase() === 'leal') {
            env.services.ui.unblock();
            p.set_amount(montoRedimir);
            let leal_redeem_data = localStorage.getItem('leal_redeem_data') ? JSON.parse(localStorage.getItem('leal_redeem_data')) : []
            for (const lr of leal_redeem_data) {
                if (lr.codigo_premio === 'DISC_LEAL' && lr.uid_customer === lealUser.uid) {
                    lr.id_premio = montoRedimir;
                }
            }
            localStorage.setItem('leal_redeem_data', JSON.stringify(leal_redeem_data));

            env.services.notification.add(
                "Se actualizó el monto del pago Leal.",
                { type: 'warning' }
            );
            return;
        }
    }

    const commerce = await env.services.pos.data.call(
        "leal.user.data",
        "search_read",
        [[['activo', '=', true]], ['uid_cms', 'id_comercio', 'nombre_comercio', 'id_sucursal', 'tiene_otp'], 0, 1],
    );
    const commerceData = commerce[0] || null;
    if (commerceData) {
        if (commerceData.tiene_otp) {
            // Solicitar OTP si el comercio tiene habilitado
            const data = {
                id_comercio: commerceData.id_comercio,
                // id_sucursal: commerceData.id_sucursal,
                id_externo: String(env.services.pos.config.id),
                uid_cms: commerceData.uid_cms,
                uid: lealUser.uid,
            };

            await env.services.pos.data.call(
                "leal.api.settings",
                "send_otp_to_customer",
                [data],
            );

            env.services.ui.unblock();
            const responseOtp = await makeAwaitable(dialog, OTPInputPopup, {
                title: _t("Ingrese OTP"),
                confirmText: _t("Validar"),
                cancelText: _t("Cancelar"),
                commerceData: commerceData
            });

            if (!responseOtp || responseOtp === undefined || responseOtp === "") {
                this.env.services.notification.add(
                    "Código OTP requerido para completar la redención Leal",
                    { type: 'warning' }
                );
                this.env.services.ui.unblock();
                return;
            }

            if (montoRedimir > 0) {
                // 1. Agregar la línea de pago primero
                // const paymentLine = currentOrder.selected_paymentline;

                // 2. Ahora, usar la línea de pago para establecer los datos y el monto
                //if (paymentLine) {
                let leal_redeem_data = [];
                leal_redeem_data.push({
                    uid_customer: lealUser.uid,
                    id_comercio: commerceData.id_comercio,
                    id_sucursal: commerceData.id_sucursal,
                    id_premio: montoRedimir,
                    codigo_premio: "DISC_LEAL",
                    otp_value: responseOtp,
                    redimido: false
                });
                localStorage.setItem('leal_redeem_data', JSON.stringify(leal_redeem_data));
                currentOrder.add_paymentline(paymentMethod);
                currentOrder.payment_ids.at(-1).set_amount(montoRedimir);
                // }
            }
            return;
        }
    }
}

export async function renewOtp(env, data_redencion) {

    const commerce = await env.services.rpc("/web/dataset/call_kw", {
        model: "leal.user.data",
        method: "search_read",
        args: [[['activo', '=', true]]],
        kwargs: {
            fields: ['uid_cms', 'id_comercio', 'nombre_comercio', 'id_sucursal', 'tiene_otp'],
            limit: 1
        }
    });
    const commerceData = commerce[0] || null;
    if (commerceData && commerceData.tiene_otp) {
        // Solicitar OTP si el comercio tiene habilitado
        const data = {
            id_comercio: commerceData.id_comercio,
            // id_sucursal: commerceData.id_sucursal,
            id_externo: String(env.services.pos.config.id),
            uid_cms: commerceData.uid_cms,
            uid: data_redencion.uid,
        };

        await env.services.rpc("/web/dataset/call_kw", {
            model: "leal.api.settings",
            method: "send_otp_to_customer",
            args: [data],
            kwargs: {}
        });
    }

    const { confirmed, payload } = await env.services.dialog.add(OTPInputPopup, {
        title: _t("Ingrese OTP"),
        confirmText: _t("Validar"),
        cancelText: _t("Cancelar"),
        commerceData: commerceData
    });

    if (!confirmed || !payload?.inputValue) return;

    data_redencion.OTP = payload?.inputValue;;
    return data_redencion;
}

export function updateProductsToCampaign(orderline) {
    if (orderline.product_id.default_code == 'DISC_LEAL') {
        return;
    }

    const ivaUnit = parseFloat(orderline.get_tax() / orderline.qty) || 0
    const data_campaign = {
        "is_campaign": true,
        "idLinea": orderline.id,
        "codigoItem": orderline.product_id.name ?? '',
        "descripcion": orderline.product_id.display_name ?? '',
        "descripcionAdicional": `Categoría ${orderline.product_id.categ_id.name}`,
        "cantidad": orderline.qty,
        "precioTotal": orderline.get_price_with_tax(),
        "precioUnidad": orderline.get_taxed_lst_unit_price(),
        "impuestoUnidad": ivaUnit,
        "tipoImpuesto": orderline.tax_ids[0].name || '0% IVA',
        "descuento": 0,
        "idExternoCategoria": "",
        "nombreCategoria": "",
        "odoo_id": orderline.id,
        "odoo_order_uuid": orderline.uuid,
    }
    let leal_campaign_redeem_data = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : []
    const exists = leal_campaign_redeem_data.find(lc => lc.idLinea === orderline.id)
    if (exists) {
        leal_campaign_redeem_data.splice(leal_campaign_redeem_data.indexOf(exists), 1);
    }
    leal_campaign_redeem_data.push(data_campaign)
    localStorage.setItem('leal_campaign_redeem_data', JSON.stringify(leal_campaign_redeem_data));
}
