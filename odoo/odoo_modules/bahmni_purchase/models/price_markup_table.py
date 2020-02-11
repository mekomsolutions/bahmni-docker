# -*- coding: utf-8 -*-
from odoo import fields, models


class PriceMarkupTable(models.Model):
    _name = 'price.markup.table'

    lower_price = fields.Float(string="Lower Price", default=1)
    higher_price = fields.Float(string="Higher Price", default=1)
    markup_percentage = fields.Float(string="Markup Percentage", default=1)
