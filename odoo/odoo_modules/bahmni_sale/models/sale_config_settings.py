# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_final_so_charge = fields.Boolean(string="Allow to enter final Sale Order charge",
                                           implied_group='bahmni_sale.group_allow_change_so_charge')
    group_default_quantity = fields.Boolean(string="Allow to enter default quantity as -1",
                                            implied_group='bahmni_sale.group_allow_change_qty')
    convert_dispensed = fields.Boolean(string="Allow to automatically convert "
                                       "quotation to sale order if drug is dispensed from local shop")
    validate_picking = fields.Boolean(string="Validate delivery when order confirmed")
    allow_negative_stock = fields.Boolean(string="Allow negative stock")
    sale_price_markup = fields.Boolean(string="Determine sale price based on cost price markup")
    auto_invoice_dispensed = fields.Boolean(string="Automatically register payment for dispensed order invoice")
    auto_create_customer_address_levels = fields.Boolean(string="Automatically create customer address for state, district, level3")

    @api.multi
    def set_convert_dispensed(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'convert_dispensed', self.convert_dispensed)

    @api.model
    def get_default_validate_picking(self, fields):
        value = int(self.env.ref('bahmni_sale.validate_delivery_when_order_confirmed').value)
        return {'validate_picking': bool(value)}

    @api.multi
    def set_default_validate_picking(self):
        for record in self:
            value = 1 if record.validate_picking else 0
            self.env.ref('bahmni_sale.validate_delivery_when_order_confirmed').write({'value': str(value)})

    @api.model
    def get_default_allow_negative_stock(self, fields):
        value = int(self.env.ref('bahmni_sale.allow_negative_stock').value)
        return {'allow_negative_stock': bool(value)}

    @api.multi
    def set_default_allow_negative_stock(self):
        for record in self:
            value = 1 if record.allow_negative_stock else 0
            self.env.ref('bahmni_sale.allow_negative_stock').write({'value': str(value)})

    @api.model
    def get_default_sale_price_markup(self, fields):
        value = int(self.env.ref('bahmni_sale.sale_price_basedon_cost_price_markup').value)
        return {'sale_price_markup': bool(value)}

    @api.multi
    def set_default_sale_price_markup(self):
        for record in self:
            value = 1 if record.sale_price_markup else 0
            self.env.ref('bahmni_sale.sale_price_basedon_cost_price_markup').write({'value': str(value)})

    @api.model
    def get_default_auto_invoice_dispensed(self, fields):
        value = int(self.env.ref('bahmni_sale.auto_register_invoice_payment_for_dispensed').value)
        return {'auto_invoice_dispensed': bool(value)}

    @api.multi
    def set_default_auto_invoice_dispensed(self):
        for record in self:
            value = 1 if record.auto_invoice_dispensed else 0
            self.env.ref('bahmni_sale.auto_register_invoice_payment_for_dispensed').write({'value': str(value)})

    @api.model
    def get_default_auto_create_customer_address_levels(self, fields):
        value = int(self.env.ref('bahmni_sale.auto_create_customer_address_levels').value)
        return {'auto_create_customer_address_levels': bool(value)}

    @api.multi
    def set_default_auto_create_customer_address_levels(self):
        for record in self:
            value = 1 if record.auto_create_customer_address_levels else 0
            self.env.ref('bahmni_sale.auto_create_customer_address_levels').write({'value': str(value)})
