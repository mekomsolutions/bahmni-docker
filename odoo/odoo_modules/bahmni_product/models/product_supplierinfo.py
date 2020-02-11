# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    manufacturer = fields.Many2one('res.partner', string="Maufacturer",
                                   domain=[('manufacturer', '=', True)])
    mrp = fields.Float(string="MRP")
