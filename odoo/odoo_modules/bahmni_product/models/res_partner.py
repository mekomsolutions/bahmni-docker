# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    manufacturer = fields.Boolean(string='Manufacturer')    # boolean field to identify manufacturers
