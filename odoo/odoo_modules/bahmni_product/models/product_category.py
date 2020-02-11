# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    uuid = fields.Char(string="UUID")

    @api.model
    def create(self, vals):
        if vals.get('uuid') is None or not vals.get('uuid'):
            vals.update({'uuid': uuid.uuid4()})
        return super(ProductCategory, self).create(vals)

# need to override this method to reverse sync updated data
#    @api.multi
#    def write(self, vals):
#        self.ensure_one()
#        return super(ProductCategory, self).create(vals)
