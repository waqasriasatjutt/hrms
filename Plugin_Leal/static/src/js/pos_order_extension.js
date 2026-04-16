import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
    },

    removeOrderline(line) {
        const lealRedeemData = localStorage.getItem('leal_redeem_data') ? JSON.parse(localStorage.getItem('leal_redeem_data')) : [];
        for (const item of lealRedeemData) {
            if (item.odoo_id === line.id && item.odoo_order_uuid === this.uuid) {
                lealRedeemData.splice(lealRedeemData.indexOf(item), 1);
                localStorage.setItem('leal_redeem_data', JSON.stringify(lealRedeemData));
                break;
            }
        }
        const lealCampaignRedeemData = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : [];
        for (const item of lealCampaignRedeemData) {
            if (item.odoo_id === line.id) {
                lealCampaignRedeemData.splice(lealCampaignRedeemData.indexOf(item), 1);
                localStorage.setItem('leal_campaign_redeem_data', JSON.stringify(lealCampaignRedeemData));
                break;
            }
        }
        super.removeOrderline(...arguments);
        return;
    }
});