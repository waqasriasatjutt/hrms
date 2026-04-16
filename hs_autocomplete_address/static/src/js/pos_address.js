/* @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { renderToString } from "@web/core/utils/render";
import { KeepLast } from "@web/core/utils/concurrency";
import { debounce } from "@web/core/utils/timing";
import { onWillUnmount, onMounted, useRef } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        
        // Only initialize for POS context to avoid multiple instances
        if (!this._isPosContext()) {
            return;
        }

        this.keepLast = new KeepLast();
        this.sessionId = this._generateUUID();
        this.is_destroyed = false;
        this.autocompleteInitialized = false;

        this._onStreetKeyUp = this._onStreetKeyUp.bind(this);
        this._onChangeStreet = debounce(this._onChangeStreet.bind(this), 200);
        this._onDocumentClick = this._onDocumentClick.bind(this);
        this.rootRef = useRef("compiled_view_root");
        
        onMounted(() => {
            if (this.rootRef.el && !this.autocompleteInitialized) {
                this.rootRef.el.addEventListener("keyup", this._onStreetKeyUp);
                document.addEventListener("click", this._onDocumentClick);
                this.autocompleteInitialized = true;
            }
        });
        
        onWillUnmount(() => {
            this.is_destroyed = true;
            if (this.rootRef.el && this.autocompleteInitialized) {
                this.rootRef.el.removeEventListener("keyup", this._onStreetKeyUp);
                document.removeEventListener("click", this._onDocumentClick);
                this.autocompleteInitialized = false;
            }
        });
    },

    _isPosContext() {
        return this.props.record && this.props.record.resModel === 'res.partner' && 
               (window.location.href.includes('/pos/') || window.location.href.includes('point_of_sale'));
    },

    _onStreetKeyUp(ev) {
        const input = ev.target;
        const streetDiv = input.closest('div[name="street"]');
        if (streetDiv && streetDiv.contains(input) && !this.is_destroyed) {
            this._onChangeStreet(ev);
        }
    },

    _onDocumentClick(ev) {
        // Close autocomplete dropdown when clicking outside
        const streetInput = ev.target.closest('div[name="street"] input');
        const dropdown = document.querySelector('.dropdown-menu.show');
        
        if (dropdown && !streetInput && !ev.target.closest('.dropdown-menu')) {
            dropdown.remove();
        }
    },

    _generateUUID: function() {
        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
            const r = (Math.random() * 16) | 0, v = c == "x" ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        });
    },

    _hideAutocomplete: function (inputContainer) {
        // Hide all autocomplete dropdowns to prevent duplicates
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => dropdown.remove());
    },

    _onChangeStreet: async function (ev) {
        let self = this;
        const inputContainer = ev.target;
        
        // Always hide existing dropdowns first
        this._hideAutocomplete(inputContainer);
        
        if (inputContainer.value && inputContainer.value.length >= 5) {
            this.keepLast.add(
                rpc('/address/autocomplete', {
                    partial_address: ev.target.value,
                    session_id: this.sessionId || null
                }).then((response) => {
                    if(response && response.results && response.results.length > 0){
                        const html = renderToString("wk_customer_address_autocomplete.AdressAutocompleteDropDown", {
                            results: response.results,
                        });
                        if(html){
                            const tempContainer = document.createElement('div');
                            tempContainer.innerHTML = html.trim();
                            const htmlElement = tempContainer.firstChild;
    
                            // Find the correct position to insert dropdown
                            const fieldWrapper = inputContainer.closest('.o_field_widget');
                            if (fieldWrapper) {
                                fieldWrapper.style.position = 'relative';
                                fieldWrapper.appendChild(htmlElement);
                            } else {
                                inputContainer.parentNode.insertAdjacentElement('afterend', htmlElement);
                            }
                            
                            htmlElement.querySelectorAll('.js_autocomplete_result').forEach((el) => {
                                el.addEventListener('click', (ev) => {
                                    self._onClickAutocompleteResult(ev);
                                });
                            });
                        }
                        if (response.session_id) this.sessionId = response.session_id;
                    }
                }).catch((error) => {
                    console.error('Address autocomplete error:', error);
                }));
        }
    },

    _onClickAutocompleteResult: async function(ev) {
        if (!this._isPosContext()) return;
        
        const dropDown = ev.currentTarget.parentNode;
        const spinner = document.createElement('div');
        dropDown.innerText = '';
        dropDown.classList.add('d-flex', 'justify-content-center', 'align-items-center');
        spinner.classList.add('spinner-border', 'text-warning', 'text-center', 'm-auto');
        dropDown.appendChild(spinner);
        
        try {
            const address = await rpc('/address/autocomplete/full',{
                address: ev.currentTarget.innerText,
                google_place_id: ev.currentTarget.dataset.googlePlaceId,
                session_id: this.sessionId || null
            });
            
            if(address && !this.is_destroyed){
                let updates = {
                    'street': address.formatted_street_number || '',
                    'city': address.city || '',
                    'zip': address.zip || '',
                    'state_id': address.state ? [address.state] : false,
                    'country_id': address.country ? [address.country] : false,
                };
                this.props.record.update(updates);
            }
        } catch (error) {
            console.error('Address details fetch error:', error);
        }
        
        dropDown.remove();
    },
});