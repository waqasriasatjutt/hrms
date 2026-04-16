/** @odoo-module **/

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { setRwCConfig, getRwCConfig } from './rwc_state';
import { triggerConfetti } from './confetti.js';


/* ---------------------------------------------
 * Minimal "$" helper (no real jQuery, only what we use)
 * ------------------------------------------- */
function $(selector) {
    const elements = Array.from(document.querySelectorAll(selector));
    return {
        elements,
        // $('#id').val() / $('#id').val('foo')
        val(value) {
            if (value === undefined) {
                const el = this.elements[0];
                return el && 'value' in el ? el.value : undefined;
            } else {
                this.elements.forEach((el) => {
                    if ('value' in el) el.value = value;
                });
                return this;
            }
        },
        // $('.class').html() / $('.class').html('<b>...')
        html(value) {
            if (value === undefined) {
                const el = this.elements[0];
                return el ? el.innerHTML : undefined;
            } else {
                this.elements.forEach((el) => {
                    el.innerHTML = value;
                });
                return this;
            }
        },
    };
}

// $.ajax({...}) using fetch under the hood
$.ajax = function (options) {
    const {
        type = "GET",
        url,
        data,
        headers = {},
        success,
        error,
    } = options || {};

    const method = type.toUpperCase();
    const fetchOptions = {
        method,
        headers: headers || {},
        credentials: "same-origin",
    };

    if (method !== "GET" && data !== undefined) {
        // data is already JSON.stringify(...) in your code
        fetchOptions.body = data;
    }

    fetch(url, fetchOptions)
        .then(async (response) => {
            const text = await response.text();
            let payload = text;
            try {
                payload = JSON.parse(text);
            } catch (_) {
                // keep text if it's not valid JSON
            }

            // Simulate jQuery behavior: call error on non-2xx
            if (!response.ok) {
                if (typeof error === "function") {
                    error({
                        status: response.status,
                        responseText: text,
                        responseJSON: typeof payload === "object" ? payload : undefined,
                    });
                }
                return;
            }

            if (typeof success === "function") {
                success(payload);
            }
        })
        .catch((err) => {
            if (typeof error === "function") {
                error({
                    status: 0,
                    responseText: String(err),
                });
            }
        });
};

const jsonrpc = async (url, params = {}) => {
    const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params,
            id: Date.now(),
        }),
    });

    const payload = await response.json();
    if (payload.error) {
        console.error("RwC jsonrpc error", payload.error);
        throw new Error(
            (payload.error.data && payload.error.data.message) ||
            payload.error.message ||
            "JSON-RPC error"
        );
    }
    return payload.result;
};

let countriesList = [];

/* ---------------------------------------------
 * Helpers / i18n (NUEVO: credenciales y utilidades)
 * ------------------------------------------- */
const BAD_CREDS_MSG = _t(
  'Bad credentials — please create your account in https://rewards.codes and enter a valid user phone and API (located at bottom of settings)'
);
window.rwcBadCreds = false;

function normalizeJSON(v) {
    try {
        if (typeof v === 'string') return JSON.parse(v);
        return v;
    } catch (_) { return null; }
}

function ensureModalMessageOrError(msg, color = 'red', style = "text-align:center;font-size:18px;") {
    // Si el modal principal está abierto, escribe ahí; si no, solo deja el flag
    const container = document.querySelector('.rwc-message');
    if (container) {
        container.innerHTML = `<div class="rwc-message" style="color:${color};${style}">${msg}</div>`;
    }
}

function extractAjaxError(xhr) {
    let payload = '';
    if (xhr && xhr.responseJSON) payload = JSON.stringify(xhr.responseJSON);
    else if (xhr && typeof xhr.responseText === 'string') payload = xhr.responseText;
    return { status: xhr?.status || 0, payload };
}

function markBadCredsIfNeeded(status, payload) {
    const looksBad =
        status === 401 || status === 403 ||
        /disallow|unauthoriz|forbid|invalid/i.test(payload || '');
    if (looksBad) {
        window.rwcBadCreds = true;
        ensureModalMessageOrError(BAD_CREDS_MSG, 'red', "text-align:center;font-size:18px;");
        return true;
    }
    return false;
}

/* ---------------------------------------------
 * Load countries (LADA)
 * ------------------------------------------- */
$.ajax({
    type: "GET",
    url: "https://apig.systems:8000/rwc-priv/get_countries",
    headers: {'Content-Type':'application/json'},
    success: function(data) {
        if (data.status === 'ok' && data.countries) {
            countriesList = data.countries;
            const rewardsSelect = document.getElementById('rewardsLadaSelect');
            if (rewardsSelect) {
                rewardsSelect.innerHTML = '';
                countriesList.forEach(country => {
                    const option = document.createElement('option');
                    option.value = country.lada;
                    option.textContent = `${country.name} (${country.lada})`;
                    rewardsSelect.appendChild(option);
                });
            }
            const codesSelect = document.getElementById('codesLadaSelect');
            if (codesSelect) {
                codesSelect.innerHTML = '';
                countriesList.forEach(country => {
                    const option = document.createElement('option');
                    option.value = country.lada;
                    option.textContent = `${country.name} (${country.lada})`;
                    codesSelect.appendChild(option);
                });
            }
        } else {
            console.log("COUNTRIES ERROR");
        }
    },
    error: function(error) {
        console.error("Error loading countries", error);
    }
});

/* ---------------------------------------------
 * Más helpers / i18n
 * ------------------------------------------- */
function translateBackendMessage(message) {
    const translations = {
        'lada is missing': _t('Missing country code'),
        'invalid code': _t('Invalid code'),
        'code sent': _t('Code sent'),
        'prize not found': _t('Prize not found. Please check balance.'),
        'max reached': _t('Points at maximum. Please redeem first.')
    };
    return translations[message] || message;
}

/* ---------------------------------------------
 * Patch Navbar
 * ------------------------------------------- */
patch(Navbar.prototype, {
    components: {
        ...Navbar.prototype.components,
    },
    setup() {
        super.setup();

        jsonrpc('/web/dataset/call_kw', {
            model: 'rewardscodes.config',
            method: 'get_all',
            args: [],
            kwargs: {},
        })
        .then(function (response) {
            const data = (typeof response === 'string') ? JSON.parse(response) : response;
            console.log("RWC DATA");
            console.log(response);
            if (!data || !data.phone || !data.mode || !data.api_key || !data.default_phone_code) {
                showError(_t("Rewards Codes has not been configured!"));
                return;
            }

            const first = (v) => Array.isArray(v) ? v[0] : v;
            const partner = first(data.phone);
            const apiKey  = first(data.api_key);
            const code    = first(data.default_phone_code);
            const mode    = first(data.mode);
            const qr      = first(data.qr);

            if ([partner, apiKey, code, qr, mode].some(v => v === undefined || v === null || (Array.isArray(v) && !v.length))) {
                showError(_t("Rewards Codes has not been configured!"));
                return;
            }

            const isDemo = !!data.demo;
            window.rwcShowTips = isDemo && !window.rwcTourDismissed;

            setRwCConfig({ partner, apiKey, code, qr, mode, demo: isDemo });

            if (window.rwcShowTips) {
                RwcTour.boot({ start: 'open' });
            }

            getRewardsLeft(partner, apiKey);
        })
        .catch(function (error) {
            showError(_t("An error occurred while retrieving Rewards Codes settings!"));
            console.error(error);
        });
    },
    onRewardsCodesButtonClick() {
        const config = getRwCConfig();

        openRewardsCodesDialog(
            config['partner'],
            config['apiKey'],
            config['code'],
            config['qr'],
            !!window.rwcShowTips
        );
        getRewardsLeft(config['partner'], config['apiKey']);

        if (window.rwcShowTips) {
            RwcTour.go('phone');
        }
    }
});

/* ---------------------------------------------
 * Modal helpers
 * ------------------------------------------- */
function closeModal(modal, { fromTour = false } = {}) {
    if (!modal) return;
    modal.classList.add('fade-out');
    // Solo detener el tour si el cierre lo hizo el usuario (no el propio tour)
    if (!fromTour && window.rwcShowTips && RwcTour && typeof RwcTour.stop === 'function') {
        RwcTour.stop({ userDismiss: true });
    }
    modal.addEventListener('animationend', () => {
        modal.remove();
    }, { once: true });
    document.body.classList.remove('modal-open');
}

function showError(message) {
    const existingModal = document.getElementById('errorModal');
    if (existingModal) existingModal.remove();

    const modal = document.createElement('div');
    modal.className = 'modal-dialog position-absolute start-0 top-0 d-flex align-items-center justify-content-center h-100 w-100 mw-100 m-0 p-0 pe-auto bg-dark bg-opacity-50';
    modal.id = 'errorModal';
    modal.setAttribute('role', 'dialog');
    modal.style.zIndex = '10001';

    const popup = document.createElement('div');
    popup.className = 'popup product-info-popup';

    const modalHeader = document.createElement('div');
    modalHeader.className = 'modal-header';
    modalHeader.style.background = 'linear-gradient(90deg, #ff416c, #ff4b2b)';
    modalHeader.style.display = 'flex';
    modalHeader.style.alignItems = 'center';
    modalHeader.style.justifyContent = 'space-between';
    modalHeader.style.padding = '12px';

    const modalTitle = document.createElement('h4');
    modalTitle.className = 'modal-title modal-rwc';
    modalTitle.textContent = `⚠️ ${_t('Error')}`;
    modalTitle.style.fontSize = '28px';

    const closeButton = document.createElement('div');
    closeButton.className = 'btn';
    closeButton.style.cursor = 'pointer';
    const closeIcon = document.createElement('i');
    closeIcon.className = 'fa fa-times';
    closeButton.appendChild(closeIcon);
    closeButton.addEventListener('click', () => closeModal(modal));

    modalHeader.appendChild(modalTitle);
    modalHeader.appendChild(closeButton);

    const modalBody = document.createElement('main');
    modalBody.className = 'body modal-body overflow-auto';

    const errorMessage = document.createElement('div');
    errorMessage.className = 'rwc-error-lbl';
    errorMessage.style.color = 'white';
    errorMessage.style.fontSize = '20px';
    errorMessage.style.textAlign = 'center';
    errorMessage.style.width = '-webkit-fill-available';
    errorMessage.style.padding = '7px';
    errorMessage.textContent = message;

    modalBody.appendChild(errorMessage);
    popup.appendChild(modalHeader);
    popup.appendChild(modalBody);
    modal.appendChild(popup);
    document.body.appendChild(modal);

    modal.classList.add('fade');
    document.body.classList.add('modal-open');
    modal.style.display = 'flex';
}

/* ---------------------------------------------
 * Build Rewards Codes dialog
 * ------------------------------------------- */
function openRewardsCodesDialog(partner, apiKey, code, qr, showTips = false) {
    document.querySelectorAll('.rwc-button').forEach(el => el.remove());
    const existingModal = document.getElementById('exampleModal');
    if (existingModal) closeModal(existingModal, { fromTour: true });

    const modal = document.createElement('div');
    modal.className = 'modal-dialog position-absolute start-0 top-0 d-flex align-items-center justify-content-center h-100 w-100 mw-100 m-0 p-0 pe-auto bg-dark bg-opacity-50';
    modal.id = 'exampleModal';
    modal.setAttribute('role', 'dialog');
    modal.style.zIndex = '10001';

    const popup = document.createElement('div');
    popup.className = 'popup product-info-popup';

    const modalHeader = document.createElement('div');
    modalHeader.className = 'modal-header';
    modalHeader.style.background = 'linear-gradient(45deg, #72246c, #9b4d9b)';
    modalHeader.style.height = '60px';
    modalHeader.style.color = 'white';
    modalHeader.style.display = 'flex';
    modalHeader.style.alignItems = 'center';
    modalHeader.style.justifyContent = 'space-between';
    modalHeader.style.padding = '14px 16px';
    modalHeader.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.25)';

    const modalTitle = document.createElement('strong');
    modalTitle.className = 'modal-title modal-rwc';
    modalTitle.textContent = _t('🎁 RwC');
    modalTitle.style.alignSelf = 'center';

    const closeButton = document.createElement('div');
    closeButton.className = 'btn rwc-close rwc-btn';
    closeButton.style.padding = '0px';
    closeButton.style.borderRadius = '50%';
    closeButton.style.alignSelf = 'center';
    closeButton.style.fontSize = '28px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.width = '40px';
    const closeIcon = document.createElement('i');
    closeIcon.className = 'fa fa-times';
    closeButton.appendChild(closeIcon);
    closeButton.addEventListener('click', () => {
        closeModal(modal);
    });

    modalHeader.appendChild(modalTitle);
    modalHeader.appendChild(closeButton);

    const modalBody = document.createElement('div');
    modalBody.className = 'modal-body';
    modalBody.style.padding = '16px';
    modalBody.style.overflowY = 'auto';
    modalBody.style.maxHeight = 'calc(100vh - 120px)';
    modalBody.style.flexGrow = '1';
    modalBody.style.backgroundColor = 'white';
    modalBody.style.display = 'flex';
    modalBody.style.flexDirection = 'column';
    modalBody.style.webkitOverflowScrolling = 'touch';

    // Rewards view
    const rewardsView = document.createElement('div');
    rewardsView.id = 'rewardsView';
    rewardsView.style.display = 'flex';
    rewardsView.style.flexFlow = 'column';
    rewardsView.style.gap = '8px';

    const rewardsPhoneLabel = document.createElement('span');
    rewardsPhoneLabel.style.fontSize = 'larger';
    rewardsPhoneLabel.style.fontWeight = 'bold';
    rewardsPhoneLabel.textContent = _t('Phone number');

    const rewardsPhoneDiv = document.createElement('div');
    rewardsPhoneDiv.style.display = 'flex';

    const rewardsLadaSelect = document.createElement('select');
    rewardsLadaSelect.id = 'rewardsLadaSelect';
    rewardsLadaSelect.style.width = '160px';
    if (countriesList && countriesList.length > 0) {
        countriesList.forEach(country => {
            let option = document.createElement('option');
            option.value = country.lada;
            option.textContent = `${country.name} (${country.lada})`;
            rewardsLadaSelect.appendChild(option);
        });
    } else {
        let option = document.createElement('option');
        option.value = '+52';
        option.textContent = `${_t('Mexico')} (+52)`;
        rewardsLadaSelect.appendChild(option);
    }
    rewardsPhoneDiv.appendChild(rewardsLadaSelect);

    const rewardsPhoneInput = document.createElement('input');
    rewardsPhoneInput.style.margin = '5px';
    rewardsPhoneInput.style.border = '1px solid #ccc';
    rewardsPhoneInput.style.borderRadius = '4px';
    rewardsPhoneInput.type = 'text';
    rewardsPhoneInput.value = "";
    rewardsPhoneInput.id = 'rewardsPhone';
    rewardsPhoneInput.style.height = '38px';
    rewardsPhoneDiv.appendChild(rewardsPhoneInput);

    rewardsView.appendChild(rewardsPhoneLabel);
    rewardsView.appendChild(rewardsPhoneDiv);

    const rewardsPointsLabel = document.createElement('span');
    rewardsPointsLabel.style.fontSize = 'larger';
    rewardsPointsLabel.style.fontWeight = 'bold';
    rewardsPointsLabel.style.marginTop = '8px';
    rewardsPointsLabel.textContent = _t('Points to add');
    rewardsView.appendChild(rewardsPointsLabel);

    const rewardsPointsDiv = document.createElement('div');
    rewardsPointsDiv.style.display = 'flex';
    rewardsPointsDiv.style.alignItems = 'center';

    const rewardsPointsInput = document.createElement('input');
    rewardsPointsInput.id = 'rewardsPoints';
    rewardsPointsInput.type = 'number';
    rewardsPointsInput.value = '1';
    rewardsPointsInput.style.margin = '5px';
    rewardsPointsInput.style.border = '1px solid #ccc';
    rewardsPointsInput.style.borderRadius = '4px';
    rewardsPointsInput.style.height = '38px';

    const rewardsButton = document.createElement('button');
    rewardsButton.className = 'rwc-btn';
    rewardsButton.id = 'rewardsButton';
    rewardsButton.type = 'button';
    rewardsButton.style.width = '280px';
    rewardsButton.textContent = _t('📞 Register number');

    rewardsPointsDiv.appendChild(rewardsPointsInput);
    rewardsPointsDiv.appendChild(rewardsButton);
    rewardsView.appendChild(rewardsPointsDiv);

    // Codes view
    const codesView = document.createElement('div');
    codesView.id = 'codesView';
    codesView.style.display = 'none';
    codesView.style.flexFlow = 'column';
    codesView.style.gap = '8px';

    const codesPhoneLabel = document.createElement('span');
    codesPhoneLabel.style.fontSize = 'larger';
    codesPhoneLabel.style.fontWeight = 'bold';
    codesPhoneLabel.textContent = _t('Phone number');

    const codesPhoneDiv = document.createElement('div');
    codesPhoneDiv.style.display = 'flex';

    const codesLadaSelect = document.createElement('select');
    codesLadaSelect.id = 'codesLadaSelect';
    codesLadaSelect.style.width = '160px';
    if (countriesList && countriesList.length > 0) {
        countriesList.forEach(country => {
            let option = document.createElement('option');
            option.value = country.lada;
            option.textContent = `${country.name} (${country.lada})`;
            codesLadaSelect.appendChild(option);
        });
    } else {
        let option = document.createElement('option');
        option.value = '+52';
        option.textContent = `${_t('Mexico')} (+52)`;
        codesLadaSelect.appendChild(option);
    }
    codesPhoneDiv.appendChild(codesLadaSelect);

    const codesPhoneInput = document.createElement('input');
    codesPhoneInput.style.margin = '5px';
    codesPhoneInput.style.border = '1px solid #ccc';
    codesPhoneInput.style.borderRadius = '4px';
    codesPhoneInput.type = 'text';
    codesPhoneInput.value = "";
    codesPhoneInput.id = 'codesPhone';
    codesPhoneDiv.appendChild(codesPhoneInput);

    const codesConsultButton = document.createElement('button');
    codesConsultButton.className = 'rwc-btn';
    codesConsultButton.id = 'codesConsultButton';
    codesConsultButton.type = 'button';
    codesConsultButton.style.width = '280px';
    codesConsultButton.textContent = _t('💳 Check balance');
    codesPhoneDiv.appendChild(codesConsultButton);

    codesView.appendChild(codesPhoneLabel);
    codesView.appendChild(codesPhoneDiv);

    const codesCodeLabel = document.createElement('span');
    codesCodeLabel.style.margin = '5px 0px';
    codesCodeLabel.style.fontSize = 'larger';
    codesCodeLabel.style.fontWeight = 'bold';
    codesCodeLabel.textContent = _t('Security code');

    const codesCodeDiv = document.createElement('div');
    codesCodeDiv.style.display = 'flex';

    const codesCodeInput = document.createElement('input');
    codesCodeInput.style.margin = '5px';
    codesCodeInput.style.border = '1px solid #ccc';
    codesCodeInput.style.borderRadius = '4px';
    codesCodeInput.type = 'text';
    codesCodeInput.id = 'codesCode';

    const codesSendButton = document.createElement('button');
    codesSendButton.className = 'rwc-btn';
    codesSendButton.id = 'codesSendButton';
    codesSendButton.type = 'button';
    codesSendButton.style.width = '280px';
    codesSendButton.textContent = _t('📤 Send code');

    codesCodeDiv.appendChild(codesCodeInput);
    codesCodeDiv.appendChild(codesSendButton);
    codesView.appendChild(codesCodeLabel);
    codesView.appendChild(codesCodeDiv);

    const codesVisitsLabel = document.createElement('span');
    codesVisitsLabel.style.margin = '5px 0px';
    codesVisitsLabel.style.fontSize = 'larger';
    codesVisitsLabel.style.fontWeight = 'bold';
    codesVisitsLabel.textContent = _t('Number of visits');

    const codesVisitsDiv = document.createElement('div');
    codesVisitsDiv.style.display = 'flex';

    const codesVisitsInput = document.createElement('input');
    codesVisitsInput.style.margin = '5px';
    codesVisitsInput.style.border = '1px solid #ccc';
    codesVisitsInput.style.borderRadius = '4px';
    codesVisitsInput.type = 'text';
    codesVisitsInput.id = 'codesVisits';

    const codesRedeemButton = document.createElement('button');
    codesRedeemButton.className = 'rwc-btn';
    codesRedeemButton.id = 'codesRedeemButton';
    codesRedeemButton.type = 'button';
    codesRedeemButton.style.width = '280px';
    codesRedeemButton.textContent = _t('🏆 Redeem prize');

    codesVisitsDiv.appendChild(codesVisitsInput);
    codesVisitsDiv.appendChild(codesRedeemButton);
    codesView.appendChild(codesVisitsLabel);
    codesView.appendChild(codesVisitsDiv);

    modalBody.appendChild(rewardsView);
    modalBody.appendChild(codesView);
    modalBody.appendChild(document.createElement('div')).className = 'rwc-message';

    const modalFooter = document.createElement('div');
    modalFooter.className = 'rwc-modal-footer';
    modalFooter.style.background = 'linear-gradient(45deg, #72246c, #9b4d9b)';
    modalFooter.style.color = 'white';
    modalFooter.style.display = 'flex';
    modalFooter.style.padding = '0px';

    const btnRewardsView = document.createElement('div');
    btnRewardsView.className = 'rwc-btn-footer';
    btnRewardsView.id = 'btnRewardsView';
    btnRewardsView.style.margin = '0';
    btnRewardsView.style.display = 'flex';
    btnRewardsView.style.justifyContent = 'center';
    btnRewardsView.style.flexGrow = '2';
    btnRewardsView.style.alignItems = 'center';
    btnRewardsView.style.fontSize = 'x-large';
    btnRewardsView.textContent = _t('🎁 Rewards');

    const btnCodesView = document.createElement('div');
    btnCodesView.className = 'rwc-btn-footer';
    btnCodesView.id = 'btnCodesView';
    btnCodesView.style.margin = '0';
    btnCodesView.style.display = 'flex';
    btnCodesView.style.justifyContent = 'center';
    btnCodesView.style.flexGrow = '2';
    btnCodesView.style.alignItems = 'center';
    btnCodesView.style.fontSize = 'x-large';
    btnCodesView.textContent = _t('💎 Codes');

    modalFooter.appendChild(btnRewardsView);
    modalFooter.appendChild(btnCodesView);

    popup.appendChild(modalHeader);
    popup.appendChild(modalBody);
    popup.appendChild(modalFooter);
    modal.appendChild(popup);
    document.body.appendChild(modal);

    modal.classList.add('fade');
    document.body.classList.add('modal-open');
    modal.style.display = 'flex';

    // Si ya se detectaron credenciales malas antes de abrir el modal
    if (window.rwcBadCreds) {
        ensureModalMessageOrError(BAD_CREDS_MSG, 'red', "text-align:center;font-size:18px;");
    }

    // --- Event listeners ---
    btnRewardsView.addEventListener('click', () => {
        rewardsView.style.display = 'flex';
        codesView.style.display = 'none';
        if (window.rwcShowTips && RwcTour.isActive()) {
            RwcTour.go('register');
            RwcTour.refresh();
        }
    });

    btnCodesView.addEventListener('click', () => {
        rewardsView.style.display = 'none';
        codesView.style.display = 'flex';
        if (window.rwcShowTips && RwcTour.isActive()) {
            RwcTour.go('codesIntro');
            RwcTour.refresh();
        }
    });

    rewardsButton.addEventListener('click', () => {
        if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; }
        const phone = document.getElementById('rewardsLadaSelect').value 
                    + document.getElementById('rewardsPhone').value;
        const points = parseInt(document.getElementById('rewardsPoints').value) || 1;
        reward(partner, phone, apiKey, points);
        if (window.rwcShowTips && RwcTour.isActive()) {
            RwcTour.go('codesIntro');
            RwcTour.refresh();
        }
    });

    codesConsultButton.addEventListener('click', () => {
        if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; }
        const phone = document.getElementById('codesLadaSelect').value 
                    + document.getElementById('codesPhone').value;
        consult(partner, phone, apiKey);
        if (window.rwcShowTips && RwcTour.isActive()) {
            RwcTour.go('sendCode');
            RwcTour.refresh();
        }
    });

    codesSendButton.addEventListener('click', () => {
        if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; }
        const phone = document.getElementById('codesLadaSelect').value 
                    + document.getElementById('codesPhone').value;
        sendCode(partner, phone, apiKey);
        if (window.rwcShowTips && RwcTour.isActive()) {
            RwcTour.go('redeem');
            RwcTour.refresh();
        }
    });

    codesRedeemButton.addEventListener('click', () => {
        if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; }
        const phoneCode = document.getElementById('codesCode').value;
        if (!phoneCode.trim()) {
            message(_t('Security code cannot be empty'), 'red');
            return;
        }
        const visits = parseInt(document.getElementById('codesVisits').value);
        if (isNaN(visits) || visits <= 0) {
            message(_t('Number of visits must be a number greater than 0'), 'red');
            return;
        }
        const phone = document.getElementById('codesLadaSelect').value 
                    + document.getElementById('codesPhone').value;
        redeem(partner, phone, phoneCode, apiKey, visits);
        if (window.rwcShowTips && RwcTour.isActive()) {
            RwcTour.go('qrPrinted');
            RwcTour.refresh();
        }
    });
}

/* ---------------------------------------------
 * API actions
 * ------------------------------------------- */
function consult(partner, customer, apiKey) {
    if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; } 
    if (customer.length < 7) {
        message(_t('The phone number is not valid'), 'red');
        return;
    }

    showLoader();

    var url = 'https://apig.systems:8000/rwc/get_phone_rewards_by_partner?id=' + partner.replace('+', '%2B');
    var body = { 'phone_id': customer };

    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(body),
        headers: { 'rwc-id': apiKey, 'Content-Type':'application/json' },
        success: function(data){
            hideLoader();
            if (data.status === 'error') {
                message(translateBackendMessage(data.message), 'red');
            } else {
                var text = `${_t('Phone')} ${customer} ${_t('has')} ${data.data.points} ${_t('points in')} ${data.data.name}</br></br>`;

                if (data.data.prizes.length > 0) {
                    text += `<span style="font-weight: bold;">${_t('Unlocked promotions')}:</span> </br>`;
                    data.data.prizes.forEach(e => {
                        text += `${e.name} (${e.quantity} ${_t('points')}): ${e.prize} </br>`;
                    });
                    text += `</br>`;
                }

                if (data.prizes_history.length > 0) {
                    text += `<span style="font-weight: bold;">${_t('History')}:</span> </br>`;
                    data.prizes_history.forEach(e => {
                        text += `${e.type} (${e.quantity} ${_t('points')}): ${e.date} </br>`;
                    });
                }
                message(text, 'black', "font-size: 18px;text-align: center;");
            }
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        },
        error: function() {
            hideLoader();
            message(_t('Network error. Please try again.'), 'red');
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        }
    });
}

function sendCode(partner, customer, apiKey) {
    if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; } 
    if (customer.length < 7) {
        message(_t('The phone number is not valid'), 'red');
        return;
    }

    showLoader();

    var url = `https://apig.systems:8000/rwc/get_phone_code_secure?id=${customer.replace('+', '%2B')}&partner_id=${partner.replace('+', '%2B')}`;

    $.ajax({
        type: "GET",
        url: url,
        headers: { 'rwc-id': apiKey, 'Content-Type':'application/json' },
        success: function(data){
            hideLoader();
            if (data.status === 'error') {
                message(translateBackendMessage(data.message), 'red');
            } else {
                message(_t('Code sent'), 'green');
            }
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        },
        error: function() {
            hideLoader();
            message(_t('Network error. Please try again.'), 'red');
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        }
    });
}

function getRewardsLeft(partner, apiKey) {
    var url = 'https://apig.systems:8000/rwc/get_rewards_left?id=' + partner.replace('+', '%2B');

    $.ajax({
        type: "GET",
        url: url,
        headers: { 'rwc-id': apiKey, 'Content-Type':'application/json' },
        success: function(data){
            data = normalizeJSON(data) || data;

            // Si el backend responde 200 pero con { error: "disallowed" }
            const errTxt = (data && (data.error || data.message)) ? String(data.error || data.message) : '';
            if (markBadCredsIfNeeded(200, errTxt)) return;

            if (!data || data.status === 'error') {
                message(translateBackendMessage(data?.message || _t('Unexpected response')), 'red');
            } else if (typeof data.rewards !== 'undefined') {
                $('.modal-rwc').html(`${data.rewards} RwC`);
            } else {
                message(_t('Unexpected response'), 'red');
            }
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        },
        error: function(xhr) {
            const { status, payload } = extractAjaxError(xhr);
            if (markBadCredsIfNeeded(status, payload)) return;
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        }
    });
}

function reward(partner, customer, apiKey, rwc) {
    if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; } 
    if (customer.length < 7) {
        message(_t('The phone number is not valid'), 'red');
        return;
    }

    showLoader();

    var url = 'https://apig.systems:8000/rwc/add_reward?id=' + partner.replace('+', '%2B');
    var body = { 'phone_id': customer, 'quantity': rwc };

    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(body),
        headers: { 'rwc-id': apiKey, 'Content-Type':'application/json' },
        success: function(data){
            hideLoader();
            if (data.status === 'error') {
                message(translateBackendMessage(data.message), 'red');
            } else {
                triggerConfetti();
                message(_t('Number registered'), 'green');
                $('#rewardsPhone').val('');
                $('#rewardsPoints').val('1');
                getRewardsLeft(partner, apiKey);
            }
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        },
        error: function() {
            hideLoader();
            message(_t('Network error. Please try again.'), 'red');
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        }
    });
}

function redeem(partner, customer, phoneCode, apiKey, rwc) {
    if (window.rwcBadCreds) { ensureModalMessageOrError(BAD_CREDS_MSG); return; } 
    if (customer.length < 7) {
        message(_t('The phone number is not valid'), 'red');
        return;
    }

    showLoader();

    var url = 'https://apig.systems:8000/rwc/add_redeem?id=' + partner.replace('+', '%2B');
    var body = {
        'body': { reference: '' },
        'phone_id': customer,
        'code': phoneCode,
        'quantity': rwc
    };

    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(body),
        headers: { 'rwc-id': apiKey, 'Content-Type':'application/json' },
        success: function(data){
            hideLoader();
            if (data.status === 'error') {
                message(translateBackendMessage(data.message), 'red');
            } else {
                triggerConfetti();
                message(_t('Redeem successful'), 'green');
                $('#codesPhone').val('');
                $('#codesCode').val('');
                $('#codesVisits').val('');
            }
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        },
        error: function() {
            hideLoader();
            message(_t('Network error. Please try again.'), 'red');
            if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
        }
    });
}

/* ---------------------------------------------
 * UI message
 * ------------------------------------------- */
function message(message, color, params = "text-align: center; font-size: 25px;") {
    const messageContainer = document.querySelector('.rwc-message');
    if (messageContainer) {
        messageContainer.innerHTML =
            `<div class="rwc-message" style="color: ${color};${params}">${message}</div>`;
        if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
    }
}

/* ---------------------------------------------
 * Loader
 * ------------------------------------------- */
function showLoader() {
    const loaderContainer = document.createElement('div');
    loaderContainer.className = 'rwc-loader-container';
    loaderContainer.innerHTML = `
        <div class="rwc-loader"><div class="rwc-loader-inner"></div></div>
        <div class="rwc-loader-text">${_t('Loading...')}</div>
    `;
    document.body.appendChild(loaderContainer);
    if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
}

function hideLoader() {
    const loaderContainer = document.querySelector('.rwc-loader-container');
    if (loaderContainer) loaderContainer.remove();
    if (window.rwcShowTips && RwcTour.isActive()) RwcTour.refresh();
}

/* =========================================================
 * RwC Guided Tour
 * ======================================================= */

const RWC_TOUR_ANCHORS = {
  open:        () => document.getElementById('rwcNavbarBtn'),
  phone:       () => document.getElementById('rewardsPhone'),
  register:    () => document.getElementById('rewardsButton'),
  codesIntro:  () => document.getElementById('btnCodesView'),
  codesPhone:  () => document.getElementById('codesPhone'),
  consult:     () => document.getElementById('codesConsultButton'),
  sendCode:    () => document.getElementById('codesSendButton'),
  redeem:      () => document.getElementById('codesRedeemButton'),
};

const RWC_TOUR_STEPS = [
  { id: 'open', where: 'top',
    text: _t('Click here to open Rewards Codes. To disable this tutorial, uncheck “Demo Mode” in POS → Configuration → RwC Configuration.'),
    guard: () => !!RWC_TOUR_ANCHORS.open(),
  },
  { id: 'phone', where: 'right',
    text: _t('Enter a customer phone to test and select its country. They will receive a WhatsApp message.'),
    guard: () => !!RWC_TOUR_ANCHORS.phone(),
    onEnter: () => { const el = RWC_TOUR_ANCHORS.phone(); if (el) el.focus(); },
  },
  { id: 'register', where: 'left',
    text: _t('Click to register 1 point and trigger the welcome flow. After, please check the phone whatsapp.'),
    guard: () => !!RWC_TOUR_ANCHORS.register(),
  },
  { id: 'codesIntro', where: 'top',
    text: _t('Switch to “Codes” to check balance and redeem prizes.'),
    guard: () => !!RWC_TOUR_ANCHORS.codesIntro(),
  },
  { id: 'codesPhone', where: 'right',
    text: _t('Enter the phone here and press “Check balance” to view points and unlocked prizes.'),
    guard: () => !!RWC_TOUR_ANCHORS.codesPhone(),
    onEnter: () => { const el = RWC_TOUR_ANCHORS.codesPhone(); if (el) el.focus(); },
  },
  { id: 'sendCode', where: 'left',
    text: _t('Send the security code to WhatsApp (verifies customer identity).'),
    guard: () => !!RWC_TOUR_ANCHORS.sendCode(),
  },
  { id: 'redeem', where: 'left',
    text: _t('Enter the number of visits and the received security code, then redeem the prize.'),
    guard: () => !!RWC_TOUR_ANCHORS.redeem(),
  },
  { id: 'qrPrinted', where: 'center', text: _t('After completing a sale, a QR is printed on the ticket. Scan it with the Rewards Codes app to view visit details.'), guard: () => true, floating: true },
];

const RwcTour = (function () {
  let state = { active:false, stepIndex:0, overlay:null, card:null, highlight:null, resizeHandler:null, mo:null, ro:null, waitTimer:null, raf1:0, raf2:0 };

  const modalEl = () => document.getElementById('exampleModal');
  const isStepFloating = (step) => !!step.floating;

  function rafReflow(fn) {
    cancelAnimationFrame(state.raf1); cancelAnimationFrame(state.raf2);
    state.raf1 = requestAnimationFrame(() => { state.raf2 = requestAnimationFrame(() => { fn(); }); });
  }

  function boot({ start = 'open' } = {}) { ensureStyles(); startTour(stepIndexBy(start)); }
  function isActive() { return !!state.active; }

  function go(id) { if (!state.active) startTour(stepIndexBy(id)); _ensureUiForStep(id); _showOrWait(stepIndexBy(id)); }
  function refresh() { if (!state.active) return; const step = RWC_TOUR_STEPS[state.stepIndex]; rafReflow(() => { const anchor = _resolveAnchor(step); _render(state.stepIndex, anchor); }); }

  function startTour(idx) { state.active = true; buildScaffold(); attachObservers(); _ensureUiForStep(RWC_TOUR_STEPS[idx].id); _showOrWait(idx); }
  function stopTour(opts = {}) {
    if (opts.userDismiss) { window.rwcTourDismissed = true; window.rwcShowTips = false; }
    detachObservers(); teardownScaffold(); _disconnectObserver(); _clearTimer();
    cancelAnimationFrame(state.raf1); cancelAnimationFrame(state.raf2); state.active = false;
  }

  function next() { const desired = Math.min(state.stepIndex + 1, RWC_TOUR_STEPS.length - 1); if (desired === state.stepIndex) { stopTour(); return; } _ensureUiForStep(RWC_TOUR_STEPS[desired].id); _showOrWait(desired); }
  function prev() { const desired = Math.max(state.stepIndex - 1, 0); _ensureUiForStep(RWC_TOUR_STEPS[desired].id); _showOrWait(desired); }

  function _ensureUiForStep(id) {
    if (id === 'open') {
      const m = modalEl();
      if (m) closeModal(m, { fromTour: true }); // ← evita matar el tour
      return;
    }
    if (!modalEl()) document.getElementById('rwcNavbarBtn')?.click();
    if (id === 'phone' || id === 'register') _switchTab('rewards');
    if (['codesIntro','codesPhone','consult','sendCode','redeem','qrPrinted'].includes(id)) _switchTab('codes');
  }

  function _switchTab(which) {
    const rewardsView = document.getElementById('rewardsView');
    const codesView   = document.getElementById('codesView');
    if (!rewardsView || !codesView) return;
    if (which === 'codes') { rewardsView.style.display = 'none'; codesView.style.display = 'flex'; }
    else { rewardsView.style.display = 'flex'; codesView.style.display = 'none'; }
  }

  function _showOrWait(idx) {
    const step = RWC_TOUR_STEPS[idx];
    const ready = step.floating ? true : !!step.guard && step.guard();
    if (!ready) { _waitForAnchor(idx); return; }
    _cancelWaiters(); const anchor = _resolveAnchor(step); _render(idx, anchor);
  }

  function _resolveAnchor(step) { if (step.floating) return null; const fn = RWC_TOUR_ANCHORS[step.id]; return fn ? fn() : null; }

  function _waitForAnchor(idx) {
    _setCardText(_t('Getting things ready…')); _disconnectObserver();
    state.mo = new MutationObserver(() => { const step = RWC_TOUR_STEPS[idx]; if (step && step.guard && step.guard()) { _disconnectObserver(); _showOrWait(idx); } });
    state.mo.observe(document.body, { childList: true, subtree: true, attributes: true });
    _clearTimer();
    state.waitTimer = setInterval(() => { const step = RWC_TOUR_STEPS[idx]; if (step && step.guard && step.guard()) { _cancelWaiters(); _showOrWait(idx); } }, 700);
  }

  function _render(idx, anchor) {
    if (!state.card || !state.highlight) return;
    state.stepIndex = idx; const step = RWC_TOUR_STEPS[idx]; step.onEnter && step.onEnter();

    if (isStepFloating(step) || !anchor) { state.highlight.style.display = 'none'; }
    else {
      const rect = anchor.getBoundingClientRect(); const pad = 6;
      state.highlight.style.display = 'block';
      state.highlight.style.left = `${rect.left + window.scrollX - pad}px`;
      state.highlight.style.top = `${rect.top + window.scrollY - pad}px`;
      state.highlight.style.width = `${rect.width + pad * 2}px`;
      state.highlight.style.height = `${rect.height + pad * 2}px`;
    }

    const card = state.card; const spacing = 12; let left, top;
    if (isStepFloating(step) || !anchor) {
      const vw = document.documentElement.clientWidth; const vh = document.documentElement.clientHeight;
      left = window.scrollX + (vw - card.offsetWidth) / 2; top = window.scrollY + (vh - card.offsetHeight) / 2;
    } else {
      const rect = anchor.getBoundingClientRect();
      left = rect.left + window.scrollX; top = rect.bottom + window.scrollY + spacing;
      if (step.where === 'top')  top = rect.top + window.scrollY - card.offsetHeight - spacing;
      if (step.where === 'left') left = rect.left + window.scrollX - Math.min(320, card.offsetWidth + spacing);
      if (step.where === 'right') left = rect.right + window.scrollX + spacing;
    }

    const minTop = window.scrollY + 96;
    const maxLeft = window.scrollX + document.documentElement.clientWidth - card.offsetWidth - 12;
    const maxTop  = window.scrollY + document.documentElement.clientHeight - card.offsetHeight - 12;

    left = Math.max(12 + window.scrollX, Math.min(left, maxLeft));
    top  = Math.max(minTop, Math.min(top,  maxTop));

    card.style.left = `${left}px`; card.style.top = `${top}px`;

    _setCardText(step.text);
    card.querySelector('.rwc-prev').disabled = (idx === 0);
    card.querySelector('.rwc-next').textContent = (idx === RWC_TOUR_STEPS.length - 1) ? _t('Finish') : _t('Next');
  }

  function _setCardText(txt) { if (!state.card) return; state.card.querySelector('.rwc-tour-body').textContent = txt; }
  function _cancelWaiters() { _disconnectObserver(); _clearTimer(); }
  function _disconnectObserver() { if (state.mo) { state.mo.disconnect(); state.mo = null; } }
  function _clearTimer() { if (state.waitTimer) { clearInterval(state.waitTimer); state.waitTimer = null; } }

  function buildScaffold() {
    const overlay = document.createElement('div'); overlay.className = 'rwc-tour-overlay'; document.body.appendChild(overlay);
    const highlight = document.createElement('div'); highlight.className = 'rwc-tour-highlight'; document.body.appendChild(highlight);
    const card = document.createElement('div'); card.className = 'rwc-tour-card';
    card.innerHTML = `
      <div class="rwc-tour-body"></div>
      <div class="rwc-tour-actions">
        <button class="rwc-tour-btn rwc-prev" type="button">${_t('Back')}</button>
        <div class="rwc-tour-spacer"></div>
        <button class="rwc-tour-btn rwc-skip" type="button">${_t('Skip')}</button>
        <button class="rwc-tour-btn rwc-next" type="button">${_t('Next')}</button>
      </div>`;
    document.body.appendChild(card);
    card.querySelector('.rwc-prev').addEventListener('click', prev);
    card.querySelector('.rwc-next').addEventListener('click', next);
    card.querySelector('.rwc-skip').addEventListener('click', () => stopTour({ userDismiss: true }));
    state.overlay = overlay; state.card = card; state.highlight = highlight;
  }

  function teardownScaffold() { [state.overlay, state.card, state.highlight].forEach(n => n && n.remove()); state.overlay = state.card = state.highlight = null; }

  function attachObservers() {
    state.resizeHandler = () => refresh();
    window.addEventListener('resize', state.resizeHandler, { passive: true });
    window.addEventListener('scroll', state.resizeHandler, { passive: true });

    if ('ResizeObserver' in window) {
      state.ro = new ResizeObserver(() => refresh()); state.ro.observe(document.body);
    }
    if (!state.mo) {
      state.mo = new MutationObserver(() => refresh()); state.mo.observe(document.body, { childList: true, subtree: true, attributes: true });
    }
  }

  function detachObservers() {
    if (state.resizeHandler) { window.removeEventListener('resize', state.resizeHandler); window.removeEventListener('scroll', state.resizeHandler); state.resizeHandler = null; }
    if (state.ro) { try { state.ro.disconnect(); } catch(e) {} state.ro = null; }
    if (state.mo) { try { state.mo.disconnect(); } catch(e) {} state.mo = null; }
  }

  function ensureStyles() {
    if (document.getElementById('rwc-tour-styles')) return;
    const css = document.createElement('style'); css.id = 'rwc-tour-styles';
    css.textContent = `
      .rwc-tour-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 200040; opacity: 0; animation: rwcFadeIn .2s ease forwards; pointer-events: none; }
      .rwc-tour-highlight { position: absolute; z-index: 200041; border-radius: 10px; box-shadow: 0 0 0 3px #ffffff, 0 0 0 9999px rgba(0,0,0,0); transition: all .18s ease; pointer-events: none; outline: 2px solid rgba(155,77,155,0.95); }
      .rwc-tour-card { position: absolute; z-index: 200042; width: min(380px, calc(100vw - 24px)); color: #fff; border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); padding: 14px; font-size: 14px; line-height: 1.35; animation: rwcPop .18s ease; transform: translateY(6px); background: linear-gradient(160deg, #72246c 0%, #9b4d9b 60%, #ab66ab 100%); border: 1px solid rgba(255,255,255,0.12); }
      .rwc-tour-body { padding: 6px 6px 10px; }
      .rwc-tour-actions { display: flex; align-items: center; gap: 8px; }
      .rwc-tour-spacer { flex: 1; }
      .rwc-tour-btn { border: none; border-radius: 10px; padding: 8px 12px; cursor: pointer; background: rgba(0,0,0,0.25); color: #fff; transition: background .15s ease, transform .05s ease; backdrop-filter: blur(2px); }
      .rwc-tour-btn:hover { background: rgba(0,0,0,0.35); }
      .rwc-tour-btn:active { transform: translateY(1px); }
      .rwc-tour-btn.rwc-next { background: linear-gradient(90deg, #9b4d9b, #72246c); }
      .rwc-tour-btn.rwc-next:hover { background: linear-gradient(90deg, #ab66ab, #7f2d79); }
      .rwc-tour-btn:disabled { opacity: .6; cursor: default; }
      @keyframes rwcFadeIn { from {opacity:0} to {opacity:1} }
      @keyframes rwcPop { from { transform: scale(.98); opacity:.9 } to { transform: scale(1); opacity:1 } }
    `;
    document.head.appendChild(css);
  }

  function stepIndexBy(id) { const i = RWC_TOUR_STEPS.findIndex(s => s.id === id); return i < 0 ? 0 : i; }
  return { boot, go, stop: stopTour, refresh, isActive };
})();

/* ---------------------------------------------
 * Base CSS (kept)
 * ------------------------------------------- */
function addCss() {
    const style = document.createElement('style');
    style.textContent = `
        .rwc-btn-navbar { background: linear-gradient(90deg, #72246c, #9b4d9b); color: #FFFFFF; border: none; padding: 8px 16px; border-radius: 6px; transition: background 0.25s ease; position: relative; overflow: visible; }
        .rwc-btn-navbar:hover { background: linear-gradient(90deg, #9b4d9b, #72246c); color: #FFFFFF; }

        .rewards { background: linear-gradient(90deg, #72246c, #9b4d9b); color: white; flex-grow: 1; border: solid 1px #bfbfbf; display: inline-block; line-height: 38px; min-width: 80px; text-align: center; border-radius: 6px; padding: 0 10px; font-size: 18px; margin-left: 6px; margin-bottom: 6px; cursor: pointer; overflow: hidden; transition: background 0.25s ease; }
        .rwc-btn { background: linear-gradient(45deg, #72246c, #9b4d9b); border: none; color: white; text-align: center; display: inline-block; font-size: 16px; margin: 4px 2px; padding: 8px 16px; border-radius: 6px; cursor: pointer; transition: background 0.25s ease; }
        .rwc-btn:hover { background: linear-gradient(45deg, #9b4d9b, #72246c); }

        .rwc-btn-footer { background: none; border: none; color: white; padding: 18px 16px; text-align: center; font-size: 16px; margin: 0; cursor: pointer; transition: background 0.25s ease; }
        .rwc-btn-footer:hover { background: rgba(255,255,255,0.1); }

        .rwc-loader-container { position: absolute; width: 100%; height: 100%; top: 0; left: 0; background: rgba(0, 0, 0, 0.7); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10002; }
        .rwc-loader { width: 80px; height: 80px; border: 6px solid transparent; border-top-color: #72246c; border-left-color: #9b4d9b; border-radius: 50%; animation: spin 1s linear infinite; position: relative; }
        .rwc-loader-inner { position: absolute; top: 5px; left: 5px; right: 5px; bottom: 5px; border: 6px solid transparent; border-top-color: #ff416c; border-left-color: #ff4b2b; border-radius: 50%; animation: spin 1.5s linear infinite reverse; }
        .rwc-loader-text { margin-top: 10px; color: white; font-size: 18px; font-family: sans-serif; }
        @keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }

        .popup.product-info-popup { border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
        .modal-dialog { border-radius: 8px !important }
        .modal-dialog.fade { animation: fadeIn 0.5s forwards; }
        .modal-dialog.fade-out { animation: fadeOut 0.5s forwards; }
    `;
    document.head.appendChild(style);
}
addCss();
