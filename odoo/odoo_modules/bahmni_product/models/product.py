# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime, date

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_quantities(self):
        res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for product in self:
            product.qty_available = res[product.id]['qty_available']
            product.incoming_qty = res[product.id]['incoming_qty']
            product.outgoing_qty = res[product.id]['outgoing_qty']
            product.virtual_available = res[product.id]['virtual_available']
            product.actual_stock = res[product.id]['actual_stock']

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        if to_date and to_date < fields.Datetime.now(): #Only to_date as to_date will correspond to qty_available
            dates_in_the_past = True
 
        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id:
            domain_quant += [('package_id', '=', package_id)]
#         if dates_in_the_past:
        domain_move_in_done = list(domain_move_out)
        domain_move_out_done = list(domain_move_in)
        domain_quant_actual_stock = copy(domain_quant)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_quant_actual_stock += ['|', '&', ('lot_id', '!=', False), '|', ('lot_id.life_date', '>=', to_date),
                                          ('lot_id.life_date', '=', False), ('lot_id', '=', False)]
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]
        else:
            domain_quant_actual_stock += ['|', '&', ('lot_id', '!=', False), '|', ('lot_id.life_date', '>=', date.today().strftime(DF)),
                                          ('lot_id.life_date', '=', False), ('lot_id', '=', False)]
        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_in
        domain_move_out_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        quants_res = dict((item['product_id'][0], item['qty']) for item in Quant.read_group(domain_quant, ['product_id', 'qty'], ['product_id'], orderby='id'))
        quants_res_actual_stock = dict((item['product_id'][0], item['qty']) for item in Quant.read_group(domain_quant_actual_stock, ['product_id', 'qty'], ['product_id'], orderby='id'))
#         if dates_in_the_past:
        # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
        if to_date:
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
        else:
            domain_move_in_done = [('state', '=', 'done')] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done')] + domain_move_out_done
        moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        res = dict()
        for product in self.with_context(prefetch_fields=False):
            res[product.id] = {}
            if dates_in_the_past:
                actual_stock = quants_res_actual_stock.get(product.id, 0.0) - moves_in_res_past.get(product.id, 0.0) + moves_out_res_past.get(product.id, 0.0)
                qty_available = quants_res.get(product.id, 0.0) - moves_in_res_past.get(product.id, 0.0) + moves_out_res_past.get(product.id, 0.0)
            else:
                qty_available = quants_res.get(product.id, 0.0)
                actual_stock = quants_res_actual_stock.get(product.id, 0.0)
            res[product.id]['qty_available'] = float_round(qty_available, precision_rounding=product.uom_id.rounding)
            res[product.id]['actual_stock'] = float_round(actual_stock, precision_rounding=product.uom_id.rounding)
            res[product.id]['incoming_qty'] = float_round(moves_in_res.get(product.id, 0.0), precision_rounding=product.uom_id.rounding)
            res[product.id]['outgoing_qty'] = float_round(moves_out_res.get(product.id, 0.0), precision_rounding=product.uom_id.rounding)
            res[product.id]['virtual_available'] = float_round(
                qty_available + res[product.id]['incoming_qty'] - res[product.id]['outgoing_qty'],
                precision_rounding=product.uom_id.rounding)
        return res

    stock_quant_ids = fields.One2many('stock.quant', 'product_id', help='Technical: used to compute quantities.')
    stock_move_ids = fields.One2many('stock.move', 'product_id', help='Technical: used to compute quantities.')
    actual_stock = fields.Integer(string="Actual Stock", compute=_compute_quantities,
                                  help="Get the actual stock available for product."
                                  "\nActual stock of product doesn't eliminates the count of expired lots from available quantities.")
    mrp = fields.Float(string="MRP")    # when variants exists for product, then mrp will be defined at variant level.
    uuid = fields.Char(string="UUID")

    @api.model
    def create(self, vals):
        if self._context.get('create_from_tmpl'):
            if vals.get('product_tmpl_id') and vals.get('attribute_value_ids'):
                if not vals.get('attribute_value_ids')[0][2]:
                    vals.update({'mrp': self.env['product.template'].browse(vals.get('product_tmpl_id')).mrp})
        product = super(ProductProduct, self.with_context(create_product_product=True,
                                                          mrp=vals.get('mrp'))).create(vals)
        # When a unique variant is created from tmpl then the standard price is set by _set_standard_price
        if not (self.env.context.get('create_from_tmpl') and len(product.product_tmpl_id.product_variant_ids) == 1):
            product._set_standard_price(vals.get('standard_price') or 0.0)
        return product

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if vals.get('mrp') and not self._context.get('write_through_tmpl'):
            if len(self.product_tmpl_id.product_variant_ids) == 1:
                self.product_tmpl_id.mrp = vals.get('mrp')
        return res

    @api.multi
    def name_get(self):
        '''inherited this method to add category name as suffix to product name
    '''
        res = super(ProductProduct, self).name_get()
        result = []
        for r in res:
            categ_name = self.browse(r[0]).categ_id.name
            result.append((r[0], r[1] + ' ('+categ_name+')'))
        return result


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self:
            template.qty_available = res[template.id]['qty_available']
            template.virtual_available = res[template.id]['virtual_available']
            template.incoming_qty = res[template.id]['incoming_qty']
            template.outgoing_qty = res[template.id]['outgoing_qty']
            template.actual_stock = res[template.id]['actual_stock']

    def _compute_quantities_dict(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = self.mapped('product_variant_ids')._product_available()
        prod_available = {}
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            actual_stock = 0
            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]
                actual_stock += variants_available[p.id]["actual_stock"]
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
                "actual_stock": actual_stock,
            }
        return prod_available

    uuid = fields.Char(string="UUID")
    mrp = fields.Float(string="MRP")
    manufacturer = fields.Many2one('res.partner', string="Manufacturer",
                                   domain=[('manufacturer', '=', True)])
    drug = fields.Char(string="Drug Name",
                       help="This field is for assigning Generic name to product")

    actual_stock = fields.Integer(string="Actual Stock", compute=_compute_quantities,
                                  help="Get the actual stock available for product."
                                  "\nActual stock of product doesn't eliminates the count of expired lots from available quantities.")
    dhis2_code = fields.Char(string="DHIS2 Code")

    @api.multi
    def action_open_quants(self):
        products = self.mapped('product_variant_ids')
        action = self.env.ref('stock.product_open_quants').read()[0]
        if self._context.get('show_actual_stock'):
            action['domain'] = ['|', '&', ('lot_id', '!=', False), '|', ('lot_id.life_date', '>=', date.today().strftime(DF)),
                                          ('lot_id.life_date', '=', False), ('lot_id', '=', False)]
            action['domain'] += [('product_id', 'in', products.ids)]
        else:
            action['domain'] = [('product_id', 'in', products.ids)]
        action['context'] = {'search_default_locationgroup': 1, 'search_default_internal_loc': 1}
        return action

    @api.model
    def create(self, vals):
        # update mrp value in template, when template is getting created through product_product object
        if self._context.get('create_product_product'):
            vals.update({'mrp': self._context.get('mrp')})
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        '''this method is inherited to set mrp price in product.product record 
        when changed in product.template, in case of no variants defined'''
        self.ensure_one()
        res = super(ProductTemplate, self).write(vals)
        if vals.get('mrp'):
            if len(self.product_variant_ids) == 1:
                # context passed while calling write of product_product,
                # as write method of product_product is also overridden to do same thing, hence to avoid recursion
                self.product_variant_ids.with_context({'write_through_tmpl': True}).write({'mrp': vals.get('mrp')})
        return res
