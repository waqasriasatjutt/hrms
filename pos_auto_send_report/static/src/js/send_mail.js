/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { rpc } from "@web/core/network/rpc";

patch(ClosePosPopup.prototype, {
    async closeSession() {
        console.log("🧾 [Custom] closeSession triggered");

//        const email = this.pos.config.send_auto_email;
//        const sessionId = this.pos.session.id;
//
//        if (email) {
//            console.log("📧 [Custom] Sending report to:", email);
//            try {
//                const result = await rpc("/send_pos_report_email", {
//                    email: email,
//                    session_id: sessionId,
//                });
//                console.log("✅ [Custom] Email sent result:", result);
//            } catch (error) {
//                console.error("❌ [Custom] Error sending email:", error);
//            }
//        } else {
//            console.warn("⚠️ [Custom] No email configured in POS settings.");
//        }

        // Call original closeSession to continue the POS flow
        await super.closeSession();
    },
});





























///** @odoo-module **/
//import { patch } from "@web/core/utils/patch";
//import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
//const { onMounted } = owl
//import { rpc } from "@web/core/network/rpc";
//
//patch(ClosePosPopup.prototype, {
//    setup() {
//        super.setup();
//        console.log("✅ ClosePosPopup patched successfully");
//    },
//
//    async sendmail() {  // 🔁 Mark function as async
//        console.log("✅ hello its me");
//        const email = this.pos.config.send_auto_email;
//        console.log("✅ Fetched company email:", email);
//
//        if (email) {
//            console.log(`📧 Sending mail to: ${email}`);
//            try {
//                const result = await rpc("/send_pos_report_email", {
//                    email: email,
//                    session_id: this.pos.session.id,
//                });
//                console.log("✅ Email sent result:", result);
//            } catch (err) {
//                console.error("❌ Failed to send email:", err);
//            }
//        } else {
//            console.log("⚠️ No email configured in POS settings.");
//        }
//    },
//    });
//    sendmail() {
//
//        console.log("✅ hello its me");
//        const email = this.pos.config.send_auto_email;
//        console.log("✅ Fetched company email:", email);
//
//        if (email) {
//            console.log(`📧 Sending mail to: ${email}`);
//                            try {
//
//                    console.log("✅ Email sent result:", result);
//                } catch (err) {
//                    console.error("❌ Failed to send email:", err);
//                }
//        } else {
//            console.log("⚠️ No email configured in POS settings.");
//        }
//    },
