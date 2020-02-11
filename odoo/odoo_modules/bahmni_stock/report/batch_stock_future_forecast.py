# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools import drop_view_if_exists


class BatchStockFutureForecast(models.Model):
    _name = 'batch.stock.future.forecast'
    _description = "Stock report by batch number considering future availabilty"
    _auto = False

    qty = fields.Float(string="Forecasted Quantity")
    location_id = fields.Many2one('stock.location', string="Location")
    product_id = fields.Many2one('product.product', string="Product")
    lot_id = fields.Many2one('stock.production.lot', string="Lot")
    
#     @api.model_cr
#     def init(self):
#         drop_view_if_exists(self.env.cr, 'batch_stock_future_forecast')
#         self.env.cr.execute("""
#             create or replace view batch_stock_future_forecast as 
#             (select max(id) as id, product_id, location_id,
#                 lot_id, sum(qty) as qty
#                 from (select max(id) as id, product_id, location_id,
#                      lot_id, sum(qty) as qty 
#                  from (select max(sm.id) as id,
#                         sm.location_id, sm.product_id,
#                         sq.lot_id, 
#                         -sum(sm.product_qty /uo.factor) as qty
#                     from stock_move as sm
#                     left join stock_quant as sq
#                         on (sq.product_id=sm.product_id)
#                     left join stock_location as source_location 
#                         on (source_location.id=sm.location_id)
#                     left join stock_location as destination_location 
#                         on (destination_location.id=sm.location_dest_id)
#                     left join product_uom uo
#                         on (uo.id=sm.product_uom)
#                     where sm.state in ('waiting', 'assigned', 'confirmed')
#                         and destination_location.usage = 'customer'
#                     group by sm.location_id, sm.product_id, sm.product_uom, sq.lot_id) 
#                 as OUT_PRODUCT group by product_id, lot_id, location_id
#                 UNION ALL
#                 select max(id) as id, product_id, location_id,
#                      lot_id, sum(qty) as qty 
#                 from (select min(sm.id) as id,
#                     sm.location_dest_id as location_id,
#                     sm.product_id, sq.lot_id,
#                     sum(sm.product_qty /uo.factor) as qty
#                     from stock_move as sm
#                     left join stock_quant as sq
#                     on (sq.product_id=sm.product_id)
#                     left join stock_location as source_location 
#                     on (source_location.id=sm.location_id)
#                     left join stock_location as destination_location 
#                     on (destination_location.id=sm.location_dest_id)
#                     left join product_uom uo
#                     on (uo.id=sm.product_uom)
#                     where sm.state in ('waiting', 'assigned', 'confirmed')
#                     and destination_location.usage != 'customer'
#                     and source_location.usage = 'supplier'
#                     group by sm.location_dest_id, sm.product_id, 
#                     sm.product_uom, sq.lot_id) as IN_PRODUCT 
#                 group by product_id, lot_id, location_id) as FINAL
#                 group by product_id, location_id, lot_id)""")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'batch_stock_future_forecast')
        self.env.cr.execute("""
            create or replace view batch_stock_future_forecast as 
            (select max(id) as id, product_id, location_id,
                lot_id, sum(qty) as qty
                from (select max(id) as id, product_id, location_id,
                     lot_id, sum(qty) as qty 
                 from (select max(sm.id) as id,
                        sm.location_id, sm.product_id,
                        sq.lot_id, 
                        -sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_quant_move_rel as sqmr 
                        on (sqmr.move_id=sm.id)
                    left join stock_quant as sq
                        on (sqmr.quant_id=sq.id)
                    left join stock_location as source_location 
                        on (source_location.id=sm.location_id)
                    left join stock_location as destination_location 
                        on (destination_location.id=sm.location_dest_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    where sm.state in ('waiting', 'assigned', 'confirmed')
                        and destination_location.usage = 'customer'
                    group by sm.location_id, sm.product_id, sm.product_uom, sq.lot_id) 
                as OUT_PRODUCT group by product_id, lot_id, location_id
                UNION ALL
                select max(id) as id, product_id, location_id,
                     lot_id, sum(qty) as qty 
                from (select min(sm.id) as id,
                    sm.location_dest_id as location_id,
                    sm.product_id, sq.lot_id,
                    sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_quant_move_rel as sqmr 
                    on (sqmr.move_id=sm.id)
                    left join stock_quant as sq
                    on (sqmr.quant_id=sq.id)
                    left join stock_location as source_location 
                    on (source_location.id=sm.location_id)
                    left join stock_location as destination_location 
                    on (destination_location.id=sm.location_dest_id)
                    left join product_uom uo
                    on (uo.id=sm.product_uom)
                    where sm.state in ('waiting', 'assigned', 'confirmed')
                    and destination_location.usage != 'customer'
                    and source_location.usage = 'supplier'
                    group by sm.location_dest_id, sm.product_id, 
                    sm.product_uom, sq.lot_id) as IN_PRODUCT 
                group by product_id, lot_id, location_id) as FINAL
                group by product_id, location_id, lot_id)""")

    @api.multi
    def unlink(self):
        raise Warning('You cannot delete any record!')