# -*- coding: utf-8 -*-
import json
import logging

from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class DrugDataService(models.Model):
    _name = 'drug.data.service'
    _auto = False
    _description = 'Intermediate Class for creating products, through api call'

    @api.model
    def create_or_update_drug_category(self, vals):
        '''Method to create or update the child product category, under drug category'''
        drug_categ = json.loads(vals.get("drug_category"))
        exist_categ = self.env["product.category"].search([('uuid', '=', drug_categ.get("id"))])
        parent_categ = self.env["product.category"].search([('name', '=', "Drug")], limit=1)
        updated_categ = self._fill_drug_category(drug_categ, parent_categ.id)
        if exist_categ:
            _logger.info("\nupdated : drug_category :\n")
            _logger.info(updated_categ)
            _logger.info(exist_categ.id)
            return exist_categ.write(updated_categ)
        _logger.info("\ninserted : drug_category :\n")
        _logger.info(updated_categ)
        return self.env['product.category'].create(updated_categ)

    @api.model
    def _fill_drug_category(self, drug_categ_from_feed, parent_id=None):
        '''Method to return values for product category record creation/updation'''
        drug_categ = {}
        drug_categ["name"] = drug_categ_from_feed.get("name")
        drug_categ["uuid"] = drug_categ_from_feed.get("id")
        if parent_id is not None:
            drug_categ["parent_id"] = parent_id

        _logger.info("drug categ in fill")
        _logger.info(drug_categ)
        return drug_categ

    @api.model
    def create_or_update_drug(self, vals):
        '''Method for creating/updating a new product under drug category'''
        products = self.env['product.product'].search([('uuid', '=', vals.get("uuid"))])
        updated_drug = self._fill_drug_object(vals, products.ids)
        if products:
            product = self.env['product.product'].browse(products.ids[0:1])
            product.write(updated_drug)
        else:
            self.env['product.product'].create(updated_drug)

    @api.model
    def _fill_drug_object(self, drug_from_feed, drug_ids_from_db):
        '''Method which returns the values for creation/updation of product under drug category'''
        drug = {}
        category_name = drug_from_feed.get("dosageForm")
        category = self.env["product.category"].search([('name', '=', category_name)])
        if category.read([]):
            category_from_db = category.read([])[0]
            categ_id = category_from_db and category_from_db.get('id') or self._create_in_drug_category(category_name)
        else:
            categ_id = self.env["product.category"].create({'name':category_name}).id

        list_price = drug_ids_from_db and self.env['product.product'].browse(drug_ids_from_db[0]).list_price or 0.0
        drug["uuid"] = drug_from_feed.get("uuid")
        drug["name"] = drug_from_feed.get("name")
        drug["default_code"] = drug_from_feed.get("shortName")
        drug["drug"] = drug_from_feed.get("genericName")
        drug["categ_id"] = categ_id
        drug["type"] = "product"
        drug["list_price"] = list_price
        drug["sale_ok"] = 1
        drug["purchase_ok"] = 1
        return drug

    @api.model
    def _create_in_drug_category(self, categ_name):
        '''Method to create a new category, while creating a product, if category does not exists'''
        parent_categ = self.env["product.category"].search([('name', '=', "Drug")])
        category = {'name': categ_name}
        if(parent_categ):
            category['parent_id'] = parent_categ.id
        return self.env['product.category'].create(category).id

