# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OrderType(models.Model):
    _name = 'order.type'

    name = fields.Char(string='Name')

    _sql_constraints = [('unique_name', 'unique(name)',
                         'Order type with this name already exists!')]

'''    @api.model
    def create(self, vals):
        if vals.get('name'):
            name = vals['name'].capitalize()
            vals.update({'name': name})
        return super(OrderType, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('name'):
            name = vals['name'].capitalize()
            vals.update({'name': name})
        return super(OrderType, self).write(vals)
'''

class OrderPickingTypeMapping(models.Model):
    _name = 'order.picking.type.mapping'

    order_type_id = fields.Many2one('order.type', string="Order Type")
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type")

    _sql_constraints = [('uniq_order_picking_type', 'unique(order_type_id, picking_type_id)',
                         'Order type and Picking type combination already exists!')]

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.order_type_id.name + ' - ' + rec.picking_type_id.name_get()[0][1]))
        return res
    
