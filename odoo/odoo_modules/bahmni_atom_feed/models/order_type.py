# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OrderType(models.Model):
    _name = 'order.type'

    name = fields.Char(string='Name')

    _sql_constraints = [('unique_name', 'unique(name)',
                         'Order type with this name already exists!')]

