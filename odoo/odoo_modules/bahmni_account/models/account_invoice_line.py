# -*- coding: utf-8 -*-
from odoo import models, api, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.model
    def create(self, vals):
        '''This method is overridden to update discount amount in invoice,
        when invoice is getting created from sale order, and discount type selected in sale order is percentage.
        Since, discount amount in readonly field and it gets updated by onchange method, which won't get called when invoice is created from backend.'''
        if vals.get('invoice_id'):
            invoice_obj = self.env['account.invoice'].browse(vals.get('invoice_id'))
            amount_untaxed = 0.0
            amount_tax = 0.0
            # calculating total from already created invoice lines.
            for ln in invoice_obj.invoice_line_ids:
                amount_untaxed += ln.price_subtotal
                taxes = ln.invoice_line_tax_ids.compute_all(ln.price_subtotal, invoice_obj.currency_id,
                                                            ln.quantity, product=ln.product_id,
                                                            partner=invoice_obj.partner_shipping_id)
                amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            if vals.get('invoice_line_tax_ids'):
                price_unit = vals.get('price_unit') * vals.get('quantity')
                if vals.get('discount'):
                    price_unit = price_unit * (1 - vals['discount']/100)
                amount_untaxed += price_unit
                tax_ids = []
                if len(vals['invoice_line_tax_ids'][0]) == 3:
                    tax_ids = vals['invoice_line_tax_ids'][0][2]
                elif len(vals['invoice_line_tax_ids'][0]) == 1:
                    tax_ids = vals['invoice_line_tax_ids'][0]
                tax_obj = self.env['account.tax'].browse(tax_ids)
                taxes = tax_obj.compute_all(price_unit, invoice_obj.currency_id,
                                            vals.get('quantity'), product=vals.get('product_id'),
                                            partner=invoice_obj.partner_id)
                amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            if invoice_obj.discount_type == 'percentage':
                discount_amount = (invoice_obj.currency_id.round(amount_untaxed) + 
                                   invoice_obj.currency_id.round(amount_tax)) * invoice_obj.discount_percentage / 100
                invoice_obj.write({'discount': discount_amount})
        return super(AccountInvoiceLine, self).create(vals)
