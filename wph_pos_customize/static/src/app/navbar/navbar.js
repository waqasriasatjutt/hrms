import {Navbar} from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

const { DateTime } = luxon;

patch(Navbar.prototype,{
    setup() {
        super.setup();
        this.state = useState({
            currentTime: DateTime.now().toFormat('dd-MM-yyyy   HH-mm-ss')
        });
        this.updateTime()
    },
    updateTime(){
        setInterval(()=> this.state.currentTime = DateTime.now().toFormat('dd-MM-yyyy   HH-mm-ss'),1000)
    }

})
