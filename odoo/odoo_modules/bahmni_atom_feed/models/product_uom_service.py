# -*- coding: utf-8 -*-
import json
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductUomService(models.Model):
    _name = 'product.uom.service'
    _auto = False

    @api.model
    def _fill_product_uom(self, product_uom_from_feed):
        product_uom = {}
        category = product_uom_from_feed.get("category")
        category_from_db = self.env["product.uom.categ"].search([('uuid', '=', category["id"])],
                                                                limit=1)

        product_uom["name"] = product_uom_from_feed.get("name")
        product_uom["uuid"] = product_uom_from_feed.get("id")
        product_uom["active"] = product_uom_from_feed.get("isActive")
        ratio = float(product_uom_from_feed.get("ratio"))
        product_uom["factor"] = 1/ratio
        product_uom["category_id"] = category_from_db.id if category_from_db else False

        uom_type = "reference"
        if ratio > 1:
            uom_type = "bigger"
        elif ratio < 1:
            uom_type = "smaller"

        product_uom["uom_type"] = uom_type
        return product_uom

    @api.model
    def create_or_update_product_uom(self, vals):
        product_uom = json.loads(vals.get("product_uom"))
        object_ids = self.env["product.uom"].with_context({"active_test": False}).search([('uuid', '=', product_uom.get("id"))], limit=1)
        uom = self._fill_product_uom(product_uom)

        if object_ids:
            return object_ids.write(uom)

        _logger.info("\ninserted : uom :\n")
        _logger.info(object_ids)
        _logger.info(uom)
        return self.env['product.uom'].create(uom)

    @api.model
    def create_or_update_product_uom_category(self, vals):
        product_uom_categ = json.loads(vals.get("product_uom_category"))
        uom_categ = {}
        uom_categ["name"] = product_uom_categ.get("name")
        uom_categ["uuid"] = product_uom_categ.get("id")
        object_ids = self.env["product.uom.categ"].search([('uuid', '=', uom_categ["uuid"])],
                                                          limit=1)

        if object_ids:
            _logger.info("\nupdated : uom_categ:\n")
            _logger.info(uom_categ)
            return object_ids.write(uom_categ)

        _logger.info("\ninserted : uom_categ:\n")
        _logger.info(uom_categ)
        return self.env['product.uom.categ'].create(uom_categ)
