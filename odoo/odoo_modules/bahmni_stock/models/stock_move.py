# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import tz

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.depends('picking_id')
    def _get_picking_time(self):
        for move in self:
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz(self._context.get('tz'))
            if move.picking_id.date:
                move_picking_date = move.picking_id.date
                utc = datetime.strptime(move_picking_date, '%Y-%m-%d %H:%M:%S')
                # Tell the datetime object that it's in UTC time zone since 
                # datetime objects are 'naive' by default
                utc = utc.replace(tzinfo=from_zone)
                # Convert time zone
                central = utc.astimezone(to_zone)
                move.stock_picking_time = datetime.strftime(central, DTF)
    
    stock_picking_time = fields.Datetime(compute=_get_picking_time,
                                         string="Stock Picking_time", store=True)
    @api.model
    def create(self,vals):
        if vals.get('origin'):
            sale_order = self.env['sale.order'].search([('name','=',str(vals.get('origin')))])
            if any(sale_order) and sale_order.location_id:
                vals.update({'location_id':sale_order.location_id.id})
        return super(StockMove,self).create(vals)
