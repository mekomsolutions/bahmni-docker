# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import drop_view_if_exists
from odoo.exceptions import Warning


class AccountCountReport(models.Model):
    _name = 'account.count.report'
    _auto = False
    _description = "Count of account heads in sale orders over a period"

    count = fields.Integer(string="Count", readonly=True)
    date = fields.Date(string="Date", readonly=True)
    account_id = fields.Many2one('account.account', string="Account")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'account_count_report')
        self.env.cr.execute("""
            create or replace view account_count_report as (
                select
                    concat(ail.account_id, '_', ai.date_invoice) as id,
                    ai.date_invoice as date,
                    ail.account_id as account_id,
                    count(*) as count
                from account_invoice ai, account_invoice_line ail
                where
                    ail.invoice_id = ai.id
                    and ai.type != 'out_refund'
                group by ail.account_id, ai.date_invoice
            )""")

    @api.multi
    def unlink(self):
        raise Warning('You cannot delete any record!')
