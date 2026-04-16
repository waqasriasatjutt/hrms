// import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
// import { patch } from "@web/core/utils/patch";

// patch(PosOrderline, {
//     extraFields: {
//         ...(PosOrderline.extraFields || {}),
//         _pinvandaag_ticket: {
//             model: "pos.order.line",
//             name: "_pinvandaag_ticket",
//             type: "char",
//             local: true,
//         }
//     }
// })

// patch(PosOrderline.prototype, {
//     setOptions(options) {
//         if (options.pinvandaag_ticket) {
//             this.update({ _pinvandaag_ticket: options.pinvandaag_ticket });
//         }
//     },
//     setTicket(ticket) {
//         this.setOptions({ pinvandaag_ticket: ticket });
//     },
//     getTicket() {
//         return this._pinvandaag_ticket;
//     }
// })
