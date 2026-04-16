/** @odoo-module **/

import { onMounted } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { Chrome } from "@point_of_sale/app/pos_app";

patch(Chrome.prototype, {
    setup() {
        super.setup();
        onMounted(() => {
            console.log("POS Screensaver initialized (Chrome mounted)");

            const pos = this?.pos ?? this?.env?.pos;
            if (!pos) {
                console.warn("POS store not found, skipping screensaver init");
                return;
            }
            const config = pos?.config || {};

            const timeout = (config.screensaver_timeout || 10) * 1000;
            const imageUrl = config.screensaver_logo
                ? `/web/image/pos.config/${config.id}/screensaver_logo`
                : '/web/static/img/logo.svg';
            const navbarLogoUrl = config.pos_navbar_logo
                ? `/web/image/pos.config/${config.id}/pos_navbar_logo`
                : false;
            const themeColor = config.pos_theme_color || "#004d99";

            console.log(`⏳ Timeout: ${timeout / 1000}s`);
            console.log(`Image: ${imageUrl}`);
            console.log(`Theme Color: ${themeColor}`);

            let idleTimer;
            let overlay;

            function createOverlay() {
                if (document.getElementById("screensaver-overlay")) return;
                overlay = document.createElement("div");
                overlay.id = "screensaver-overlay";
                overlay.style.cssText = `
                    display:none;
                    position:fixed;
                    top:0; left:0;
                    width:100%; height:100%;
                    background: ${themeColor};
                    z-index:9999;
                    justify-content:center;
                    align-items:center;
                    flex-direction:column;
                    transition: opacity 0.5s ease-in-out;
                `;
                overlay.innerHTML = `
                    <img src="${imageUrl}" 
                         style="max-width:60%;max-height:60%;object-fit:contain;filter: drop-shadow(0 0 20px rgba(255,255,255,0.3));">
                    <small style="margin-top:25px;color:rgba(255,255,255,0.7);font-style:italic;">
                        Press any key or move mouse to resume
                    </small>
                `;
                document.body.appendChild(overlay);
                console.log("Screensaver overlay created");
            }

            function resetTimer() {
                clearTimeout(idleTimer);
                if (overlay) {
                    overlay.style.opacity = "0";
                    setTimeout(() => (overlay.style.display = "none"), 200);
                }
                idleTimer = setTimeout(() => {
                    if (overlay) {
                        overlay.style.display = "flex";
                        setTimeout(() => (overlay.style.opacity = "1"), 50);
                        console.log("Screensaver activated");
                    }
                }, timeout);
            }

            function applyBranding() {
                // Apply theme color to POS Navbar
                const navbar = document.querySelector(".pos-topheader") || document.querySelector(".pos-navbar");
                if (navbar) {
                    navbar.style.backgroundColor = themeColor;
                    navbar.style.borderBottom = "none";
                }

                // Apply Navbar Logo
                if (navbarLogoUrl) {
                    const logoImg = document.querySelector(".pos-logo") || document.querySelector(".pos-centerheader img");
                    if (logoImg) {
                        logoImg.src = navbarLogoUrl;
                        logoImg.style.maxHeight = "40px";
                    }
                }
            }

            createOverlay();
            // Try immediately
            applyBranding();

            // Re-apply on UI changes to ensure it sticks
            window.addEventListener("transitionend", applyBranding);
            // Polling backup for initial load
            let brandingInterval = setInterval(applyBranding, 1000);
            setTimeout(() => clearInterval(brandingInterval), 10000);

            window.addEventListener("mousemove", resetTimer);
            window.addEventListener("keydown", resetTimer);
            window.addEventListener("click", resetTimer);
            resetTimer();
        });
    },
});
