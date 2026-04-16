import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useState, Component, onWillStart, onWillDestroy } from "@odoo/owl";

const { DateTime } = luxon;

export class CustomerDisplayQRPopup extends Component {
  static template = "pos_qr30_scb.CustomerDisplayQRPopup";
  static components = { Dialog };
  static props = {
    qrCode: String,
    shopName: String,
    amount: String,
    expireTime: Date,
  };

  static defaultProps = {
    title: _t("Mobile Banking"),
  };

  setup() {
    super.setup();

    this.props.body = _t("Please scan the QR code with %s", this.props.title);
    this.props.expireTime = DateTime.fromJSDate(this.props.expireTime);

    this.state = useState({
      secondBeforeExpire: 600,
    });

    this.update = setInterval(() => {
      this.countdown();
    }, 1000);

    onWillDestroy(() => clearInterval(this.update));
  }

  countdown() {
    this.state.secondBeforeExpire = Math.round(
      this.props.expireTime.diffNow("seconds").seconds
    );
    if (this.state.secondBeforeExpire <= 0) {
      this.props.close();
    }
  }
}
