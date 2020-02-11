# -*- coding: utf-8 -*-
from odoo import models, fields


class product_product(models.Model):
    _inherit = 'product.product'

    def get_mrp(self, supplier_id, prod_qty, date=False, uom_id=False):
        '''Method which will return mrp for an product from Vendor configuration if set,
            else will return mrp configured in product master'''
        seller = self._select_seller(partner_id=supplier_id,
                                     quantity=self.product_qty,
                                     date=date,
                                     uom_id=uom_id)
        if seller:
            mrp = seller.mrp
        else:
            mrp = self.mrp
        return mrp

    def set_mrp(self, supplier_id, product_qty, mrp, price_unit, date=False, uom_id=False):
        '''Method which will add vendor configuration if does not exists, 
            if exists it will set mrp in that.'''
        seller = self._select_seller(partner_id=supplier_id,
                                     quantity=self.product_qty,
                                     date=date,
                                     uom_id=uom_id)
        if seller:
            seller.mrp = mrp
        else:
            max_seq = self.env['product.supplierinfo'].search([], order='sequence desc', limit=1)
            sequence = max_seq + 1
            self.env['product.supplierinfo'].create({'product_tmpl_id': self.product_tmpl_id.id,
                                                     'name': supplier_id,
                                                     'min_qty': product_qty,
                                                     'price': price_unit,
                                                     'mrp': mrp,
                                                     'sequence': sequence})

    def _check_low_stock(self):
        if self.type == 'product':
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)])
            location_ids = [wh.lot_stock_id.id for wh in warehouse]
            if self._context.get('location'):
                location_ids = [self._context.get('location')]
            for location in location_ids:
                orderpoint = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', self.id),
                                                                            ('location_id', '=', location)])
                if orderpoint.product_min_qty > self.with_context({'location': location}).virtual_available:
                    self.low_stock = True
                    return True
        self.low_stock = False

    def _search_low_stock(self, operator, value):
        '''Method to return products which are having low stock available in warehouse, w.r.t. reordering rule defined'''
        ids = set()
        ctx = self._context.copy() or {}
        location = ctx.get('location', False)
        location_condition = ""
        if(location):
            location_condition = "where location_id=%d"%(location)
        else:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)])
            location_ids = [wh.lot_stock_id.id for wh in warehouse]
            if len(location_ids) > 1:
                location_condition = "where location_id in %s"%(tuple(location_ids))
            elif len(location_ids) == 1:
                location_condition = "where location_id=%d"%(location_ids[0])
        self._cr.execute("select product_id from stock_warehouse_orderpoint " + location_condition)
        product_ids = set(p_id[0] for p_id in self._cr.fetchall())
        for product in self.with_context({'context': ctx}).browse(list(product_ids)):
            orderpoints = sorted(product.orderpoint_ids, key=lambda orderpoint: orderpoint.product_min_qty, reverse=True)
            if (len(orderpoints) > 0 and product.virtual_available < orderpoints[0].product_min_qty):
                ids.add(product.id)
        if ids:
            if operator == '=':
                return [('id', 'in', list(ids))]
            elif operator == '!=':
                return [('id', 'not in', list(ids))]

    low_stock = fields.Boolean(compute=_check_low_stock, search=_search_low_stock, string="Low Stock")
