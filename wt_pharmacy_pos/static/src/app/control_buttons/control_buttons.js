import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { patch } from "@web/core/utils/patch";

debugger
patch(ControlButtons.prototype, {
	async clickPrescriptions() {
        const self = this
		const order = this.pos.get_order();
		if (!this.partner) {
			this.dialog.add(AlertDialog, {
                title: _t("No Patient Selected"),
                body: _t(
                    "Please select a patient (customer) before loading a prescription."
                ),
            });
            return;
        }
        const pharmacy_prescription = await this.pos.data.searchRead(
            "pharmacy.prescription",
            [["state", "=", "draft"],["patient_id", "=", this.partner.id]],
            ['id','name', 'patient_id', 'doctor_id', 'prescription_date'],
            {}
        );

        if(!pharmacy_prescription.length){
        	this.dialog.add(AlertDialog, {
                title: _t("No Prescription"),
                body: _t(
                    "No prescription found for selected patient."
                ),
            });
            return;
        }
        // this.pos.models["pharmacy.prescription"].getAll()
        const partners = this.pos.models['res.partner']
        const prescriptionList = pharmacy_prescription.map((prescription) => ({
            id: prescription.id,
            label: prescription.name,
            description: _t(`Data: ${prescription.prescription_date}, Doctor: ${partners.get(prescription.doctor_id)?.name}`),
            item: prescription,
            isSelected: prescription.id === order.prescription_id,
        }));

        const selectedPrescription = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select Prescription"),
            list: prescriptionList,
        });
        if (!selectedPrescription) {
            return false;
        }

        const prescription_line = await this.pos.data.searchRead(
            "pharmacy.prescription.line",
            [["prescription_id", "=", selectedPrescription.id]],
            ['id','drug_id', 'quantity', 'notes'],
            {}
        );
        order.set_prescription(selectedPrescription)

        prescription_line.forEach(async (line) => {
            let product = self.pos.models["product.product"].get(line.drug_id)
            if(product) {
                let order_line = await self.pos.addLineToCurrentOrder({
                    product_id: product,
                    qty: line.quantity,
                    customer_note: line.notes,
                });
            }else{
                console.warn(`Product with ID ${line.drug_id[0]} not found in POS.`);
            }
        });
	}
});