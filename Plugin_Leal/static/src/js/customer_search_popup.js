/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useState } from "@odoo/owl";
export class CustomerSearchPopup extends Component {
    static template = "Plugin_Leal.CustomerSearchPopup";
    static components = { Dialog };
    static defaultProps = {
        confirmText: _t("Seleccionar"),
        cancelText: _t("Cancelar"),
        title: _t("Buscar Cliente en Leal"),
        body: _t("Ingrese el número de documento para buscar:"),
    };
    setup() {
        super.setup();
        this.pos = usePos();
        this.state = useState({
            inputValue: "",
            searchResults: [],
            isLoading: false,
            selectedCustomer: null,
            hasSearched: false,
            errorMessage: ""
        });
        this.searchTimeout = null;
    };
    async confirm() {
        this.props.getPayload(this.state);
        this.props.close();
    };

    onClose() {
        this.props.close();
    };
    async onInputChange(event) {
        this.state.inputValue = event.target.value;
        this.state.errorMessage = "";

        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // If input has 3 or more characters, search after 300ms delay for better UX
        if (this.state.inputValue.trim().length >= 3) {
            // Show loading state immediately for better user feedback
            this.state.isLoading = true;
            this.searchTimeout = setTimeout(() => {
                this.performSearch();
            }, 300);
        } else {
            // Clear results if less than 3 characters
            this.state.searchResults = [];
            this.state.hasSearched = false;
            this.state.selectedCustomer = null;
            this.state.isLoading = false;
        }
    }

    onInputKeydown(event) {
        if (event.key === "Enter" && this.state.selectedCustomer) {
            this.confirm();
        }
    }

    async performSearch() {
        if (this.state.inputValue.trim().length < 3) {
            return;
        }

        this.state.isLoading = true;
        this.state.hasSearched = true;
        this.state.errorMessage = "";

        try {
            const searchQuery = this.state.inputValue.trim();
            const result = await this.pos.data.call(
                "leal.api.settings",
                "search_customer",
                [searchQuery]
            );

            if (result.success) {
                // If the API returns an array of customers
                if (Array.isArray(result.data)) {
                    this.state.searchResults = result.data;
                } else if (result.data && typeof result.data === 'object') {
                    // If the API returns a single customer object, wrap it in an array
                    this.state.searchResults = [result.data];
                } else {
                    this.state.searchResults = [];
                }
            } else {
                this.state.searchResults = [];
                this.state.errorMessage = result.message || "No se encontraron resultados";
            }
        } catch (error) {
            console.error("Error searching customers:", error);
            this.state.searchResults = [];
            this.state.errorMessage = "Error al buscar clientes. Intente nuevamente.";
        } finally {
            this.state.isLoading = false;
        }
    }

    selectCustomer(customer) {
        this.state.selectedCustomer = customer;
        // You could also auto-confirm here if desired
        this.confirm();
    }

    get isConfirmDisabled() {
        return !this.state.selectedCustomer;
    }

    get displayNoResults() {
        return this.state.hasSearched &&
            !this.state.isLoading &&
            this.state.searchResults.length === 0 &&
            this.state.inputValue.trim().length >= 3;
    }
}