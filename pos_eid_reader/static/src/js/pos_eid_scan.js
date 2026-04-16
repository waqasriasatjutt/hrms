/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { markup } from "@odoo/owl";

// Patch PartnerList to add Scan ID functionality
patch(PartnerList.prototype, {
    async scanEidAndCreatePartner() {
        try {
            // Show loading notification
            this.notification.add(_t("Scanning eID card..."), { type: "info" });

            let response;
            try {
                response = await fetch("http://127.0.0.1:8765/read-eid");
            } catch (e) {
                // Network error - bridge not running - show dialog with clickable link
                this.dialog.add(AlertDialog, {
                    title: _t("eID Bridge Not Found"),
                    body: markup(_t('Cannot reach eID bridge. Please download and install it from:<br/><br/><a href="https://gitlab.com/imran.afr/odoo-module-eid-reader/-/blob/main/eid_bridge.exe" target="_blank" style="color: #007bff; text-decoration: underline;">Download eID Bridge</a>')),
                });
                return;
            }
            
            if (!response.ok) {
                this.notification.add(
                    _t("Error: eID bridge error. Make sure eID card is inserted and the bridge application is running."),
                    { type: "danger" }
                );
                return;
            }

            const data = await response.json();

            if (data.status !== "success") {
                // Bridge is running but returned an error (no card, read error, etc.)
                const errorMsg = data.message || "";
                if (errorMsg.toLowerCase().includes("no card") || errorMsg.toLowerCase().includes("not found") || errorMsg.toLowerCase().includes("insert")) {
                    this.notification.add(
                        _t("No eID card detected. Please insert your Belgian eID card and try again."),
                        { type: "warning" }
                    );
                } else {
                    this.notification.add(
                        data.message || _t("eID scan failed. Please try again."),
                        { type: "danger" }
                    );
                }
                return;
            }

            const identity = data.identity || {};
            const address = data.address || {};
            const nationalNumber = identity.national_number || "";

            // Check if customer with this national number already exists
            if (nationalNumber) {
                const existingPartners = await this.pos.data.call(
                    "res.partner",
                    "search_read",
                    [[["ref", "=", nationalNumber]]],
                    { fields: ["id", "name"], limit: 1 }
                );

                if (existingPartners && existingPartners.length > 0) {
                    // Customer already exists - load and open for editing
                    const existingPartnerData = await this.pos.data.read("res.partner", [existingPartners[0].id]);
                    const existingPartner = existingPartnerData[0];
                    
                    this.notification.add(
                        _t("Customer '%s' already exists. Opening for editing...", existingPartners[0].name),
                        { type: "info" }
                    );

                    // Open the edit form for the existing partner
                    const updatedPartner = await this.editPartner(existingPartner);

                    // Select the partner
                    if (updatedPartner) {
                        this.clickPartner(updatedPartner);
                    } else {
                        this.clickPartner(existingPartner);
                    }
                    return;
                }
            }

            // Build the name
            const name = `${identity.first_names || ""} ${identity.surname || ""}`.trim() || "New Customer";

            // Prepare partner data
            const partnerData = {
                name: name,
            };

            if (address.street_and_number) {
                partnerData.street = address.street_and_number;
            }
            if (address.zip_code) {
                partnerData.zip = address.zip_code;
            }
            if (address.municipality) {
                partnerData.city = address.municipality;
            }
            if (this.pos.company.country_id?.id) {
                partnerData.country_id = this.pos.company.country_id.id;
            }
            if (nationalNumber) {
                partnerData.ref = nationalNumber;
            }
            if (data.photo) {
                partnerData.image_1920 = data.photo;
            }

            // First create the partner with scanned data
            const partnerId = await this.pos.data.call(
                "res.partner",
                "create",
                [partnerData]
            );

            // Read the created partner
            const newPartners = await this.pos.data.read("res.partner", [partnerId]);
            const newPartner = newPartners[0];

            this.notification.add(_t("eID scanned! You can now add more details..."), { type: "success" });

            // Open the edit form for the newly created partner so user can add email, phone, etc.
            const updatedPartner = await this.editPartner(newPartner);

            // Select the partner (either updated or original if user discarded)
            if (updatedPartner) {
                this.clickPartner(updatedPartner);
            } else {
                this.clickPartner(newPartner);
            }

        } catch (error) {
            console.error("eID scan error:", error);
            this.notification.add(
                error.message || _t("eID scan failed"),
                { type: "danger" }
            );
        }
    },
});