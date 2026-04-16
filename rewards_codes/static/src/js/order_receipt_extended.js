/** @odoo-module **/

import { OrderReceipt } from '@point_of_sale/app/screens/receipt_screen/receipt/order_receipt';
import { patch } from '@web/core/utils/patch';
import { useRef, onMounted, useState, onWillUnmount } from '@odoo/owl';
import { getQRData, setQRData } from './rwc_state';

patch(OrderReceipt.prototype, {
    setup() {
        super.setup();

        const qrData = getQRData();
        console.log("RWC QR DATA");
        console.log(qrData);
        // If `disabled` is true, return immediately
        if (qrData && qrData['disabled']) {
            this.state = useState({ qr: false });
            return;
        }

        this.state = useState({ qr: true });  // Set `qr` to true if not disabled

        const qrCodeContainerRef = useRef('qr-code-container');

        // Use default empty strings if properties are missing in `qrData`
        const partner = encodeURIComponent(qrData?.['partner'] || '');
        const code = qrData?.['code'] || '';
        const quantity = qrData?.['quantity'] || '';

        // Set qrUrl to an empty string if all values are empty
        const qrUrl = partner || code || quantity
            ? `https://app.rewards.codes/?id=${partner}&code=${code}&quantity=${quantity}&qr=one_use`
            : '';

        // Helper function to poll for canvas existence
        function convertCanvasToImg(container, attempt = 0) {
            const canvas = container.querySelector('canvas');
            if (canvas) {
                try {
                    const dataUrl = canvas.toDataURL();
                    const img = document.createElement('img');
                    img.src = dataUrl;
                    img.alt = 'QR Code';
                    // Ensure the image is fully loaded before replacing content
                    img.onload = () => {
                        container.innerHTML = '';
                        container.appendChild(img);
                        console.log("QR code image loaded and set.");
                    };
                } catch (error) {
                    console.error("Error converting canvas to image:", error);
                }
            } else if (attempt < 10) {
                // Try again after 100ms (up to 1 second total)
                setTimeout(() => convertCanvasToImg(container, attempt + 1), 100);
            } else {
                console.warn("Canvas not found after multiple attempts.");
            }
        }

        onMounted(() => {
            if (qrUrl) {  // Only create the QR code if qrUrl is not empty
                const container = qrCodeContainerRef.el;
                new QRCode(container, {
                    text: qrUrl,
                    // width: 160,
                    // height: 160,
                });
                // Poll for the canvas and then replace it with an image
                convertCanvasToImg(container);
            }
        });

        // Clean up the listener when the component is unmounted
        onWillUnmount(() => {
            setQRData({});
            console.log("RESET STATE");
        });
    },
});

console.log("OrderReceipt Patched");