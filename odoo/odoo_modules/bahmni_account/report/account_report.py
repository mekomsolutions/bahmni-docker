# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import drop_view_if_exists


class AccountReport(models.Model):
    _name = 'account.report'
    _description = "Account reports for actual & received amount"
    _auto = False

    actual_amount = fields.Integer(string="Expenses")
    amount_received = fields.Integer(string="Collections")
    date = fields.Date(string="Date")
    account_id = fields.Many2one('account.account', string="Account Head")
    
    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'account_report')
        self.env.cr.execute("""
            create or replace view account_report as (
              (select id,date,account_id, sum(actual_amount) as actual_amount,sum(amount_received) as amount_received
               from (
               SELECT
                 pg_catalog.concat(ail.account_id, '_', ai.date_invoice, '_', ai.type) AS id,ai.id as invoice_id,
                 ai.date_invoice AS date,
                 ail.account_id,
                 CASE
                 WHEN ai.type = 'out_refund' THEN 0
                 ELSE sum(ail.price_subtotal)
                 END AS actual_amount,
                 CASE
                 WHEN ai.type = 'out_refund' THEN sum(
                     (-ail.price_subtotal) * (ai.amount_total / (ai.amount_tax + ai.amount_untaxed)))
                 ELSE sum(ail.price_subtotal * (ai.amount_total / (ai.amount_tax + ai.amount_untaxed)))
                 END AS amount_received
               FROM account_invoice ai, account_invoice_line ail
               WHERE ail.invoice_id = ai.id AND (ai.amount_tax + ai.amount_untaxed) <> 0 AND state = 'paid'
               GROUP BY ail.account_id, ai.date_invoice, ai.type, ai.id
               UNION
               SELECT
                 pg_catalog.concat(ail.account_id, '_', ai.date_invoice, '_', ai.type) AS id,ai.id as invoice_id,
                 ai.date_invoice AS date,
                 ail.account_id,
                 CASE
                 WHEN ai.type = 'out_refund' THEN 0
                 ELSE max(ai.amount_total)
                 END AS actual_amount,
                 CASE
                 WHEN ai.type = 'out_refund' THEN max(ai.amount_total) * -1
                 ELSE max(ai.amount_total)
                 END AS amount_received
               FROM account_invoice ai, account_invoice_line ail
               WHERE ail.invoice_id = ai.id AND (ai.amount_tax + ai.amount_untaxed) = 0 AND state = 'paid'
                     and ail.account_id not in
                         (select id from account_account where name in ('FINE','Discount','Overcharge'))
               GROUP BY ail.account_id, ai.date_invoice, ai.type,ai.id
               UNION
               SELECT
                 pg_catalog.concat(ail.account_id, '_', ai.date_invoice, '_', ai.type) AS id,ai.id as invoice_id,
                 ai.date_invoice AS date,
                 ail.account_id,
                 CASE
                 WHEN ai.type = 'out_refund' THEN 0
                 ELSE sum(ai.amount_total)
                 END AS actual_amount,
                 CASE
                 WHEN ai.type = 'out_refund' THEN sum(-ai.amount_total)
                 ELSE sum(ai.amount_total)
                 END AS amount_received
               FROM account_invoice ai, account_invoice_line ail
               WHERE ail.invoice_id = ai.id AND (ai.amount_tax + ai.amount_untaxed) = 0 AND state = 'paid'
                     and ail.account_id in
                         (select id from account_account where name in ('FINE','Discount','Overcharge'))
               GROUP BY ail.account_id, ai.date_invoice, ai.type,ai.id
             ) as r group by id,date,account_id)
            )""")
