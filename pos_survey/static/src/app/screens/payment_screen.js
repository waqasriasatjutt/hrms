import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";


patch(PaymentScreen.prototype, {
    async afterOrderValidation() {
        // if the order synced, the id (that was initially a string) 
        // will be replaced with the server id (a number) 
        if (!isNaN(this.currentOrder.id && this.currentOrder.survey_answers.length>0)) {
            this.pos.data.call("pos.order", "process_survey", [
                this.currentOrder.id,
                this.currentOrder.survey_answers,
            ]);
        }
        
        return super.afterOrderValidation(...arguments)
    },
})
