import json

from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon
# from odoo.addons.pos_qr30_scb.tests.common import TestPosQr30Common


@tagged('post_install', '-at_install')
class TestPoSControllerQr30(TestPointOfSaleHttpCommon):

    def test_payment_callback(self):
        """This test make sure that proper message is broadcasted to the POS when a payment is done.
        """
        notification_data = {
            'payerAccountNumber': "0123456",
            'payerName': "Test partner",
            'sendingBankCode': "014",
            'amount': "45.67",
            'transactionId': "Test transaction",
            'transactionDateandTime': "2024-12-07T05:16:48.000+07:00",
            'billPaymentRef1': "ref1_test",
            'billPaymentRef2': "ref2_test",
            'billPaymentRef3': "ref3_test",
            'currencyCode': "764"
        }

        response = self.url_open(f'/pos_qr/notification', data=json.dumps(notification_data),
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode('utf-8'))

        # should response with the transactionId
        self.assertEqual(response_data.get('transactionId'), notification_data['transactionId'])

        bus_1 = self.env['bus.bus'].sudo().search(
            [('channel', 'like', 'qr30_payment_callback')],
            order='id desc',
            limit=1,
        )

        payload_1 = json.loads(bus_1.message)['payload']
        result = json.loads(payload_1)

        # the message should be broadcasted to the POS
        self.assertEqual(result.get('billPaymentRef1'), notification_data['billPaymentRef1'])
        self.assertEqual(result.get('billPaymentRef2'), notification_data['billPaymentRef2'])
        self.assertEqual(result.get('billPaymentRef3'), notification_data['billPaymentRef3'])
