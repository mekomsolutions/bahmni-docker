# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class SaleShop(models.Model):
    _name = "sale.shop"
    _description = "Sales Shop"

    name = fields.Char('Shop Name', size=64, required=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    location_id = fields.Many2one('stock.location', 'Location')
    payment_default_id = fields.Many2one('account.payment.term', 'Default Payment Term', required=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    project_id = fields.Many2one('account.analytic.account', 'Analytic Account')#domain=[('parent_id', '!=', False)]
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda self: self.env['res.company']._company_default_get('sale.shop')) 
