# -*- coding: utf-8 -*-
import json
import logging

from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class ReferenceDataService(models.Model):
    _name = 'reference.data.service'
    _auto = False
    _description = 'Intermediate Class for creating products, through api call'

    @api.model
    def create_or_update_ref_data(self, vals, category_name):
        product_obj = self.env["product.product"].with_context(
            {"active_test": False}).search([('uuid', '=', vals.get("uuid"))], limit=1)
        updated_data = self._fill_data(vals, category=category_name)
        if product_obj:
            product_obj.write(updated_data)
        else:
            self.env['product.product'].create(updated_data)

    @api.model
    def _fill_data(self, vals, category=None):
        data = {}
        category_name = category if category else "Others"
        category_hierarchy = self._get_category_hierarchy(category_name)
        specified_product_category = vals.get("product_category")
        if specified_product_category:
            category_name = specified_product_category
        _logger.info("\n******* Creating Product with Category: %s, hierarchy: %s", category_name, category_hierarchy)
        category_obj = self.env['product.category'].search([('name', '=', category_name)])
        if category_obj.read():
            category_from_db = category_obj.read()[0]
            categ_id = category_from_db and category_from_db.get('id') or \
                       self._create_category_in_hierarchy(category_name, category_hierarchy).id
        else:
            categ_id = self.env['product.category'].create({'name': category_name}).id

        data["uuid"] = vals.get("uuid")
        data["name"] = vals.get("name")
        data["active"] = vals.get("is_active")
        data["categ_id"] = categ_id
        data["sale_ok"] = vals.get("is_active")
        data["purchase_ok"] = False
        data["type"] = "service"
        return data

    @api.model
    def _get_category_hierarchy(self, category):
        if category == 'Radiology':
            return ["Services", "All Products"]
        elif category == 'Test':
            return ["Lab", "Services", "All Products"]
        elif category == 'Panel':
            return ["Lab", "Services", "All Products"]
        else:
            return ["Services", "All"]

    @api.model
    def _create_category_in_hierarchy(self, category_name, category_hierarchy):
        _logger.info("\n creating product category %s, under hierarchy %s", category_name, category_hierarchy)
        if len(category_hierarchy) > 0:
            category_ids = self.env['product.category'].search([('name', '=', category_hierarchy[0])]).ids
            if len(category_ids) > 0:
                parent_id = category_ids[0]
            else:
                parent_category_name = category_hierarchy[0]
                del category_hierarchy[0]
                parent_id = self._create_category_in_hierarchy(parent_category_name, category_hierarchy)
            return self.env['product.category'].create({'name': category_name,
                                                        'parent_id': parent_id})
        else:
            return self.env['product.category'].create({'name': category_name})
