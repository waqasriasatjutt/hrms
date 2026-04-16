# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@tagged('post_install', '-at_install')
class TestPosQr30Common(TestPointOfSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # add env on cls and many other things

        print("set up")
        print(cls)
        # cls.receivable_account = cls.env['account.account'].create({
        #     'name': 'POS Receivable QR30',
        #     'code': 'X1012.POS.QR30',
        #     'account_type': 'asset_receivable',
        #     'internal_group': 'asset',
        #     'reconcile': True,
        # })

        # cls.qr30_payment_method = cls.env['pos.payment.method'].create({
        #     'name': 'Qr30',
        #     'journal_id': cls.company_data['default_journal_bank'].id,
        #     'receivable_account_id': cls.receivable_account.id,
        #     'company_id': cls.env.company.id,
        #     'payment_method_type': 'qr_code',
        #     'qr_code_method': 'qr30',

        #     'qr30_biller_name': 'Test Biller',
        #     'qr30_biller_code': '123456',
        #     'qr30_has_callback': True,
        # })

        # create the data for each tests. By doing it in the setUpClass instead
        # of in a setUp or in each test case, we reduce the testing time and
        # the duplication of code.
        # cls.notification_data = {
        #     'reference': cls.reference,
        #     'payment_details': '1234',
        #     'simulated_state': 'done',
        # }
        print("set up completa")

    @classmethod
    def tearDownClass(cls):
        cls.env['pos.payment.method'].search([('name', '=', 'Qr30')]).unlink()
