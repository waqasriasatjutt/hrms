import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {

    async addProductToOrder(...args) {
        const is_restrict_negative = this?.pos?.config?.is_restrict_negative
        const quantityByProductTmplId = this?.state?.quantityByProductTmplId
        const quantityAddedByproduct = quantityByProductTmplId[args['0']?.product_tmpl_id.id]
        const is_storable = args['0']?.is_storable
        if (is_restrict_negative && is_storable && (args['0'].qty_available <= 0 || quantityAddedByproduct >= args['0'].qty_available)){
            this.dialog.add(AlertDialog, {
                    title: _t("Insufficient Stock"),
                    body: _t(`Stock limit reached for ${args['0'].name}. Available quantity: ${args['0'].qty_available}.`),
                });
        }
        else{
            await super.addProductToOrder(...args)
        }
    },
    
});
