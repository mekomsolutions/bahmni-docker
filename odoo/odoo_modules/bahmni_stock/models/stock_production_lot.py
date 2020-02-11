# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def name_get(self):
        '''name_get method is overridden to view expiry date in many2one field of lot'''
        if self._context is None:
            context = {}
        else:
            context = self._context.copy()
        res = []
        for record in self:
            name = record.name
            if(record.life_date):
                expiry_date = datetime.strptime(record.life_date, '%Y-%m-%d %H:%M:%S')
                expiry = expiry_date.strftime("%b %d,%Y")
                name = "%s [%s]" % (name, expiry)
            if(context.get('show_future_forcast', False)):
                name = "%s %s" % (name, record.future_stock_forecast)
            res.append((record.id, name))
        return res
    
    @api.depends('product_id')
    def _get_future_stock_forecast(self):
        """ Gets stock of products for locations
        @return: Dictionary of values
        """
        for lot in self:
            if self._context is None:
                context = {}
            else:
                context = self._context.copy()
            if 'location_id' not in context or context['location_id'] is None:
                locations = self.env['stock.location'].search([('usage', '=', 'internal')])
            elif context.get('search_in_child', False):
                locations = self.env['stock.location'].search([('location_id', 'child_of', context['location_id'])]) or [context['location_id']]
            else:
                context['location_id'] = 15
                locations = self.env['stock.production.lot'].browse(context.get('location_id'))
            if locations:
                self._cr.execute('''select
                        lot_id,
                        sum(qty)
                    from
                        stock_quant
                    where
                        location_id IN %s and lot_id = %s 
                        group by lot_id''',
                        (tuple(locations.ids), lot.id,))
                result = self._cr.dictfetchall()
                if result and result[0]:
                    lot.stock_forecast = result[0].get('sum')

                    product_uom_id = context.get('product_uom', None)
                    if(product_uom_id):
                        product_uom = self.env['product.uom'].browse(product_uom_id)
                        lot.stock_forecast = result[0].get('sum') * product_uom.factor

    sale_price = fields.Float(string="Sale Price")
    mrp = fields.Float(string="MRP")
    cost_price = fields.Float(string="Cost Price")
    stock_forecast = fields.Float(string="Available forecast",
                                     compute=_get_future_stock_forecast,
                                     digits=dp.get_precision('Product Unit of Measure'),
                                     help="Future stock forecast quantity of products with this Serial Number available in company warehouses",
                                     )
    