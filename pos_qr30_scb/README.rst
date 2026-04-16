Point of Sale QR30 Integration - SCB
====================================

The Point of sale QR30 module provides integration with SCB’s qr code
payment service via Thai QR Code Tag 30 (QR 30). It allows the POS
system to validate a customer payment with the callback url from the
bank when a customer pays by scanning a QR code with a Thai bank’s
mobile application.

This module collects the following data from the bank. Please check the
PDPA law.

-  Transaction id
-  Payer’s bank
-  Payer account name
-  Payer account number

Supported features
------------------

-  Direct payment flow
-  Automatic payment confirmation
-  Manual payment confirmation
-  Payment limits (min-max)
-  Payment fee
-  QR code on Customer Display

Technical details
-----------------

API: `SCB Standard Checkout <https://developer.scb.co.th/#/documents/documentation/qr-payment/thai-qr.html>`_

SDK: `SCB Development App <https://developer.scb.co.th/#/documents/documentation/basics/getting-started.html>`_

This module requires API key and secret from SCB. You should register
with SCB to get them.

When the Send button is clicked, a server-to-server API call is made to
create the qr code. When the payment is made, the system receives
notification from SCB via a callback endpoint(/pos_qr/notification) and
the payment is confirmed automatically.

The payment confirmation is sent to a web client via webhook. Make sure
the proxy allows this.

Compatibility
~~~~~~~~~~~~~

-  Odoo 18

Configuration
-------------

First, you need to create a payment for POS. To configure this module,
you need to:

-  Go to Point of Sale > Configuration > Payment Methods > New

   |Configuration|

-  Original setup

   -  Set the method name
   -  Assign a journal
   -  Integration: Select “Bank App (QR Code)”
   -  QR Code Format: Select “QR Tag 30”

-  Additional setup

   -  “Bank” is fixed as SCB.
   -  “Name” can be shop name or any text you want to display with the
      QR code.
   -  “Enable Callback” is to allow callback from SCB.
   -  “Callback URL” is the callback endpoint in Odoo system. Copy the
      generated value and put it in SCB configuration.
      |SCB Configuration|
   -  “Biller ID” is provided by SCB in merchant profile menu.
   -  “Ref 3 Prefix” is also in merchant profile.

   -  “API Key” is from Application menu.
   -  “API Secret” is also from application.

   -  “Base url” is the url prefix to the endpoints. The default value
      is for sandbox environment.

   -  “Customer Fee” is the service charge for this payment. Set it as
      you’d like.
   -  “Fix Payment Product” is the product to associate with “Customer
      Fee”. You can create a new service type product. This product
      appears in the receipt.
 
      |Receipt|

-  (Optional) Click Test Connection to test the configuration.

-  Add this new payment method to your Point of Sale shop.

Usage
-----

To use this payment,

-  After checking out, select the payment method associated with QR tag
   30 and click send.
   
   |Select Payment Method|

-  The qrcode popup will appears.

   |QR Code popup|

- After the payment is confirmed, the system will automatically navigate to receipt screen.

  - User can hide the popup and process another order while waiting for payment. In this case, the payment is marked as paid and the user can click on "Validate" to proceed to receipt screen.
  - User can confirm the payment manually by clicking on the "Manually confirm payment" button.

- The difference of closing and cancel button in qrcode popup.

  - Closing popup with (X) in the top right corner is just hiding the popup. You can reopen it with the same QR code data. Customer can still pay with the same qrcode.
  - Cancel Payment button however, voids the qr code. If the user make a payment, it does NOT register within the system. You can generate a new QR code.

To view payment history,

Go to Point of Sale > Orders > SCB Payment History

-  Here you can see a list of payments made group by their payment method

-  Click to view full information

   |Full payment history|

Module history
--------------

-  ``18.0``

   -  Released

Testing instructions
--------------------

Payments must be made using a separate `sandbox account <https://developer.scb.co.th/#/management/apps>`_.

Read more at https://developer.scb.co.th/#/documents.

.. |Configuration| image:: https://raw.githubusercontent.com/ncharlie/pos_qr30/refs/heads/18.0/pos_qr30_scb/static/description/setup1.png 
 :alt: Configuration 
 :width: 800
.. |SCB Configuration| image:: https://raw.githubusercontent.com/ncharlie/pos_qr30/refs/heads/18.0/pos_qr30_scb/static/description/setup2.png
 :alt: SCB Configuration
 :width: 350
.. |Receipt| image:: https://raw.githubusercontent.com/ncharlie/pos_qr30/refs/heads/18.0/pos_qr30_scb/static/description/receipt1.png
 :alt: Receipt
 :width: 400
.. |Select Payment Method| image:: https://raw.githubusercontent.com/ncharlie/pos_qr30/refs/heads/18.0/pos_qr30_scb/static/description/usage1.png
 :alt: Select Payment Method
 :width: 800
.. |QR Code popup| image:: https://raw.githubusercontent.com/ncharlie/pos_qr30/refs/heads/18.0/pos_qr30_scb/static/description/usage2.png
 :alt: QR Code popup
 :width: 800
.. |Full payment history| image:: https://raw.githubusercontent.com/ncharlie/pos_qr30/refs/heads/18.0/pos_qr30_scb/static/description/history1.png
 :alt: Full payment history
 :width: 450
