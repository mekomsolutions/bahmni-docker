# -*- coding: utf-8 -*-
from collections import namedtuple

from odoo import fields, models, api
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    # this method is overridden to update cost_price, sale_price and mrp while lot is getting created
    def _create_lots_for_picking(self):
            Lot = self.env['stock.production.lot']
            for pack_op_lot in self.mapped('pack_operation_ids').mapped('pack_lot_ids'):
                if not pack_op_lot.lot_id:
                    lot = Lot.create({'name': pack_op_lot.lot_name, 
                                      'product_id': pack_op_lot.operation_id.product_id.id,
                                      'life_date': pack_op_lot.expiry_date,
                                      'cost_price': pack_op_lot.cost_price,
                                      'sale_price': pack_op_lot.sale_price,
                                      'mrp': pack_op_lot.mrp})
                    pack_op_lot.write({'lot_id': lot.id})
            # TDE FIXME: this should not be done here
            self.mapped('pack_operation_ids').mapped('pack_lot_ids').filtered(lambda op_lot: op_lot.qty == 0.0).unlink()
            
    @api.multi
    def do_prepare_partial(self):
        # TDE CLEANME: oh dear ...
        PackOperation = self.env['stock.pack.operation']

        # get list of existing operations and delete them
        existing_packages = PackOperation.search([('picking_id', 'in', self.ids)])  # TDE FIXME: o2m / m2o ?
        if existing_packages:
            existing_packages.unlink()
        for picking in self:
            forced_qties = {}  # Quantity remaining after calculating reserved quants
            picking_quants = self.env['stock.quant']
            # Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                if move.state not in ('assigned', 'confirmed', 'waiting'):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = 0.0
                if move.state == 'assigned':
                    qty = move.product_uom._compute_quantity(move.product_uom_qty, move.product_id.uom_id, round=False)
                    forced_qty = qty - sum([x.qty for x in move_quants])
                # if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
                if float_compare(forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding) > 0:
                    if forced_qties.get(move.product_id):
                        forced_qties[move.product_id] += forced_qty
                    else:
                        forced_qties[move.product_id] = forced_qty
            for vals in picking._prepare_pack_ops(picking_quants, forced_qties):
                vals['fresh_record'] = False
                product_available_qty = self.env['product.product'].with_context({'location': vals.get('location_id')}).browse(vals.get('product_id')).qty_available
                vals.update({'picking_type': picking.picking_type_id.code,
                             'available_qty': product_available_qty})
                PackOperation |= PackOperation.create(vals)
        # recompute the remaining quantities all at once
        self.do_recompute_remaining_quantities()
        for pack in PackOperation:
            pack.ordered_qty = sum(
                pack.mapped('linked_move_operation_ids').mapped('move_id').filtered(lambda r: r.state != 'cancel').mapped('ordered_qty')
            )
        self.write({'recompute_pack_op': False})
    
    # this method is overridden to update available qty for lot, and expiration date, when automatically reserved
    def _prepare_pack_ops(self, quants, forced_qties):
        """ Prepare pack_operations, returns a list of dict to give at create """
        # TDE CLEANME: oh dear ...
        valid_quants = quants.filtered(lambda quant: quant.qty > 0)
        _Mapping = namedtuple('Mapping', ('product', 'package', 'owner', 'location', 'location_dst_id'))

        all_products = valid_quants.mapped('product_id') | self.env['product.product'].browse(p.id for p in forced_qties.keys()) | self.move_lines.mapped('product_id')
        computed_putaway_locations = dict(
            (product, self.location_dest_id.get_putaway_strategy(product) or self.location_dest_id.id) for product in all_products)

        product_to_uom = dict((product.id, product.uom_id) for product in all_products)
        picking_moves = self.move_lines.filtered(lambda move: move.state not in ('done', 'cancel'))
        for move in picking_moves:
            # If we encounter an UoM that is smaller than the default UoM or the one already chosen, use the new one instead.
            if move.product_uom != product_to_uom[move.product_id.id] and move.product_uom.factor > product_to_uom[move.product_id.id].factor:
                product_to_uom[move.product_id.id] = move.product_uom
        if len(picking_moves.mapped('location_id')) > 1:
            raise UserError(_('The source location must be the same for all the moves of the picking.'))
        if len(picking_moves.mapped('location_dest_id')) > 1:
            raise UserError(_('The destination location must be the same for all the moves of the picking.'))

        pack_operation_values = []
        # find the packages we can move as a whole, create pack operations and mark related quants as done
        top_lvl_packages = valid_quants._get_top_level_packages(computed_putaway_locations)
        for pack in top_lvl_packages:
            pack_quants = pack.get_content()
            pack_operation_values.append({
                'picking_id': self.id,
                'package_id': pack.id,
                'product_qty': 1.0,
                'location_id': pack.location_id.id,
                'location_dest_id': computed_putaway_locations[pack_quants[0].product_id],
                'owner_id': pack.owner_id.id,
            })
            valid_quants -= pack_quants

        # Go through all remaining reserved quants and group by product, package, owner, source location and dest location
        # Lots will go into pack operation lot object
        qtys_grouped = {}
        lots_grouped = {}
        for quant in valid_quants:
            key = _Mapping(quant.product_id, quant.package_id, quant.owner_id, quant.location_id, computed_putaway_locations[quant.product_id])
            qtys_grouped.setdefault(key, 0.0)
            qtys_grouped[key] += quant.qty
            if quant.product_id.tracking != 'none' and quant.lot_id:
                lots_grouped.setdefault(key, dict()).setdefault(quant.lot_id.id, 0.0)
                lots_grouped[key][quant.lot_id.id] += quant.qty
        # Do the same for the forced quantities (in cases of force_assign or incomming shipment for example)
        for product, qty in forced_qties.items():
            if qty <= 0.0:
                continue
            key = _Mapping(product, self.env['stock.quant.package'], self.owner_id, self.location_id, computed_putaway_locations[product])
            qtys_grouped.setdefault(key, 0.0)
            qtys_grouped[key] += qty

        # Create the necessary operations for the grouped quants and remaining qtys
        Uom = self.env['product.uom']
        product_id_to_vals = {}  # use it to create operations using the same order as the picking stock moves
        for mapping, qty in qtys_grouped.items():
            uom = product_to_uom[mapping.product.id]
            val_dict = {
                'picking_id': self.id,
                'product_qty': mapping.product.uom_id._compute_quantity(qty, uom),
                'product_id': mapping.product.id,
                'package_id': mapping.package.id,
                'owner_id': mapping.owner.id,
                'location_id': mapping.location.id,
                'location_dest_id': mapping.location_dst_id,
                'product_uom_id': uom.id,
                'pack_lot_ids': [
                    (0, 0, {
                        'lot_id': lot,
                        'available_qty': self.env['product.product'].with_context({'location': mapping.location.id,
                                                                                   'lot_id': lot}).browse(mapping.product.id).qty_available,
                        'expiry_date': self.env['stock.production.lot'].browse(lot).life_date,
                        'qty': 0.0,
                        'qty_todo': mapping.product.uom_id._compute_quantity(lots_grouped[mapping][lot], uom)
                    }) for lot in lots_grouped.get(mapping, {}).keys()],
            }
            product_id_to_vals.setdefault(mapping.product.id, list()).append(val_dict)

        for move in self.move_lines.filtered(lambda move: move.state not in ('done', 'cancel')):
            values = product_id_to_vals.pop(move.product_id.id, [])
            pack_operation_values += values
        return pack_operation_values
        
    @api.model
    def create(self,vals):
        picking_obj = super(StockPicking,self).create(vals)
        if picking_obj.origin:
            sale_order = self.env['sale.order'].search([('name','=',str(picking_obj.origin))])
            if any(sale_order) and sale_order.location_id:
                picking_obj.location_id = sale_order.location_id.id
        return picking_obj
