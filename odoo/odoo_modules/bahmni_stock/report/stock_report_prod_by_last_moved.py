# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import drop_view_if_exists
from odoo.exceptions import Warning


class prod_last_moved_report(models.Model):
    _name = "prod_last_moved.report"
    _description = "Products report by last moved"
    _auto = False
    _order = 'last_moved_date desc'

    product_id = fields.Many2one('product.product', string="Product",
                                 readonly=True)
    origin = fields.Text(string="Origin", readonly=True)
    location_id = fields.Many2one('stock.location', string="Source Location",
                                  readonly=True)
    location_dest_id = fields.Many2one('stock.location',
                                       string="Destination Location")
    last_moved_date = fields.Datetime(string="Last Moved Date")
    
    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'prod_last_moved_report')
        self.env.cr.execute("""
            create or replace view prod_last_moved_report as (
                SELECT
                  sm.id,
                  sm.name AS desc,
                  sm.origin,
                  sm.location_id,
                  sm.location_dest_id,
                  sm.product_id,
                  stock_picking_time AS last_moved_date
                FROM stock_move sm
                    JOIN (
                           SELECT
                             max(id) AS id
                           FROM stock_move osm
                           WHERE (product_id, stock_picking_time) IN
                                 (SELECT
                                    sm.product_id,
                                    max(sm.stock_picking_time)
                                  FROM stock_move sm
                                  GROUP BY product_id)
                           GROUP BY product_id) AS csm
                      ON sm.id = csm.id
            )""")

    @api.multi
    def unlink(self):
        raise Warning('You cannot delete any record!')
