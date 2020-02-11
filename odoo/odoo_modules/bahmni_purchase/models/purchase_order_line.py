# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.tools import SUPERUSER_ID, DEFAULT_SERVER_DATETIME_FORMAT as DTF


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mrp = fields.Float(string="MRP")
    manufacturer = fields.Many2one('res.partner', string="Manufacturer",
                                   domain=[('manufacturer', '=', True)])
    prod_categ_id = fields.Many2one('product.category', string='Product Category')

    @api.onchange('product_id')
    def onchange_product_id(self):
        '''Set product category in purchase order line, on change of product_id'''
        result = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            self.prod_categ_id = self.product_id.categ_id.id
        return result

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        '''Method to get mrp for product from vendor configuration in product master'''
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)
        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DTF)

        if not seller:
            self.mrp = self.product_id.mrp
            return
        self.manufacturer = seller.manufacturer.id
        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
        mrp = self.env['account.tax']._fix_tax_included_price_company(seller.mrp, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)
        if mrp and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            mrp = seller.currency_id.compute(mrp, self.order_id.currency_id)
        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)
        if mrp and self.product_uom and seller.product_uom != self.product_uom:
            mrp = seller.product_uom._compute_price(mrp, self.product_uom)
        self.price_unit = price_unit
        self.mrp = mrp
