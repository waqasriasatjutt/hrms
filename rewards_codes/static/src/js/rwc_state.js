/** @odoo-module **/

import { reactive } from '@odoo/owl';

const rwcState = reactive({
    qrData: null,
    config: null,
});

export function setQRData(data) {
    rwcState.qrData = data;
}

export function getQRData() {
    return rwcState.qrData;
}

export function setRwCConfig(data) {
    rwcState.config = data;
}

export function getRwCConfig() {
    return rwcState.config;
}