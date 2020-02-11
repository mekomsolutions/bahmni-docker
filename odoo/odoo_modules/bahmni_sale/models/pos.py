from odoo import fields, models, api, _

class PosOrder(models.Model):
    _inherit = 'pos.order'

    shop_id = fields.Many2one('sale.shop', 'Shop' )

class PosConfig(models.Model):
    _inherit = 'pos.config'
	
    shop_id = fields.Many2one('sale.shop', 'Shop')

