# -*- coding: utf-8 -*-

from odoo import fields, models, _

class DojoTransaction(models.Model):
    _name = "dojo.transaction"
    _rec_name = 'transactionId'

    order_id = fields.Many2one(
        comodel_name='pos.order',
    )
    transactionId = fields.Char(
        string='Transaction ID'
    )
    transactionTime = fields.Datetime(
        string='Transaction Time'
    )
    transactionType = fields.Char(
        string='Transaction Type'
    )
    transactionNumber = fields.Char(
        string='Transaction Number'
    )
    authCode = fields.Char(
        string='AuthCode'
    )
    amountTotal = fields.Float(
        string='Amount',
        digits=0
    )
    transactionResult = fields.Char(
        string='Status'
    )