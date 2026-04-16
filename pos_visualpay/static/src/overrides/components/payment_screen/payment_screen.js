import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { VisualPayPopup } from "@pos_visualpay/app/visualpay_popup/visualpay_popup";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.visualPayOnHoldCreated = false;
        // Guardará {order_uuid: [{image, comment}, {image, comment}, ...]}
        this.visualPayEvidence = {};
    },

    async validateOrder(isForceValidate) {
        const onHoldLines = this.paymentLines.filter(
            (l) => l.payment_method_id.payment_method_type === "visualpay"
        );
        this.visualPayOnHoldCreated = onHoldLines.length > 0;

        if (!this.visualPayOnHoldCreated || await this.confirmVisualPayOnHold(onHoldLines)) {
            await super.validateOrder(...arguments);

            const id = this.currentOrder?.id;
            if (!id) return;

            try {
                const evidences = this.visualPayEvidence[this.currentOrder.uuid] || [];
                if (!evidences.length) return;

                let body = "Pagos realizados:<br>";
                const attachmentIds = [];

                const csrfToken =
                    window.odoo?.csrf_token ||
                    document.querySelector('meta[name="csrf_token"]')?.getAttribute("content");

                // 🔹 Subimos todas las imágenes y formamos el cuerpo del mensaje
                for (const ev of evidences) {
                    body += `Pago realizado con <b>${ev.name || 'Método Desconocido'}</b><br>`;
                    // Subir imagen (si hay)
                    if (ev?.image) {
                        const formData = new FormData();
                        formData.append("csrf_token", csrfToken);
                        formData.append("thread_model", "pos.order");
                        formData.append("thread_id", id);
                        formData.append(
                            "ufile",
                            this.dataURLtoBlob(`data:image/jpeg;base64,${ev.image}`),
                            "evidencia_visualpay.jpg"
                        );

                        const uploadResp = await fetch("/mail/attachment/upload", {
                            method: "POST",
                            body: formData,
                            credentials: "include",
                        });

                        const uploadData = await uploadResp.json();

                        if (uploadData?.data?.["ir.attachment"]?.length) {
                            const attachment = uploadData.data["ir.attachment"][0];
                            attachmentIds.push(attachment.id);
                        }
                    }

                    // Agregar comentario al cuerpo
                    if (ev?.comment) {
                        body += `Comentario: ${ev.comment} <br>`;
                    }
                }

                // 🔹 Enviar mensaje único con todas las evidencias y adjuntos
                await this.env.services.orm.call("pos.order", "message_post", [[id]], {
                    body,
                    message_type: "comment",
                    subtype_xmlid: "mail.mt_comment",
                    attachment_ids: attachmentIds,
                    body_is_html: true, // o body_has_html: true según versión
                });
                this.notification.add("✅ Se guardaron las evidencias en la orden", { type: "success" });
            } catch (e) {
                this.notification.add("Error al enviar mensaje", { type: "danger" });
            }
        }
    },

    // 📦 helper para convertir base64 a Blob
    dataURLtoBlob(dataurl) {
        const arr = dataurl.split(",");
        const mime = arr[0].match(/:(.*?);/)[1];
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);
        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], { type: mime });
    },

    async confirmVisualPayOnHold(onHoldLines) {
        if (!this.currentOrder?.id) {
            this.dialog.add(AlertDialog, {
                title: _t("Pago no disponible"),
                body: _t("La orden seleccionada no existe."),
            });
            return false;
        }

        return new Promise((resolve) => {
            if (!this.visualPayOnHoldCreated) return resolve(false);

            // 🆕 Un solo popup que maneja todas las líneas VisualPay
            this.dialog.add(VisualPayPopup, {
                lines: onHoldLines,
                order: this.currentOrder,
                onConfirm: (dataList) => {
                    // dataList será [{ line_id, image, comment }, ...]
                    this.visualPayEvidence[this.currentOrder.uuid] = dataList;
                    resolve(true);
                },
                onCancel: () => resolve(false),
            });
        });
    }

});
