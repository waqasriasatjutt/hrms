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
import { rpc } from "@web/core/network/rpc"

patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        this.keepLast = new KeepLast();
        this.sessionId = this._generateUUID();
        this.is_destroyed = false;

        this._onStreetKeyUp = this._onStreetKeyUp.bind(this);
        this._onChangeStreet = debounce(this._onChangeStreet.bind(this), 200);
        this.rootRef = useRef("compiled_view_root");
        onMounted(() => {
            if (this.rootRef.el) {
                this.rootRef.el.addEventListener("keyup", this._onStreetKeyUp);
            }
        });
        onWillUnmount(() => {
            this.is_destroyed = false;
            if (this.rootRef.el) {
                this.rootRef.el.removeEventListener("keyup", this._onStreetKeyUp);
            }
        });
    },
    _onStreetKeyUp(ev) {
        const input = ev.target;
        const streetDiv = input.closest('div[name="street"]');
        if (streetDiv && streetDiv.contains(input) && !this.is_destroyed) {
            this._onChangeStreet(ev);
        }
    },
    /**
     * Used to generate a unique session ID for the places API.
     *
     * @private
    */
    _generateUUID: function() {
        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        const r = (Math.random() * 16) | 0, v = c == "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
        });
    },
    _hideAutocomplete: function (inputContainer) {
        const dropdown = inputContainer.parentNode.parentNode.querySelector('.dropdown-menu');
        if (dropdown) dropdown.remove();
    },
    _onChangeStreet: async function (ev) {
        let self = this;
        const inputContainer = ev.target;
        if (inputContainer.value && inputContainer.value.length >= 5) {
            this.keepLast.add(
                rpc('/address/autocomplete', {
                    partial_address: ev.target.value,
                    session_id: this.sessionId || null
                }).then((response) => {
                    this._hideAutocomplete(inputContainer);
                    if(response && response.results){
                        const html = renderToString("wk_customer_address_autocomplete.AdressAutocompleteDropDown", {
                            results: response.results,
                        });
                        if(html){
                            const tempContainer = document.createElement('div');
                            tempContainer.innerHTML = html.trim();
                            const htmlElement = tempContainer.firstChild;

                            inputContainer.parentNode.insertAdjacentElement('afterend', htmlElement);
                            htmlElement.querySelectorAll('.js_autocomplete_result').forEach((el) => {
                                el.addEventListener('click', (ev) => {
                                    self._onClickAutocompleteResult(ev);
                                });
                            });
                        }
                        if (response.session_id) this.sessionId = response.session_id;
                    }
                }));
        } else this._hideAutocomplete(inputContainer);
    },
    _onClickAutocompleteResult: async function(ev) {
        const dropDown = ev.currentTarget.parentNode;
        const spinner = document.createElement('div');
        dropDown.innerText = '';
        dropDown.classList.add('d-flex', 'justify-content-center', 'align-items-center');
        spinner.classList.add('spinner-border', 'text-warning', 'text-center', 'm-auto');
        dropDown.appendChild(spinner);

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
        dropDown.remove();
    },
});
