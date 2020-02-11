# -*- coding: utf-8 -*-
from datetime import datetime
import json
from itertools import groupby
import logging

from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.exceptions import Warning

ORDER_DISPENSED_FALSE = 'false'  # type: str

_logger = logging.getLogger(__name__)


class OrderSaveService(models.Model):
    _name = 'order.save.service'
    _auto = False

    def _get_openerp_orders(self, vals):
        if not vals.get("orders", None):
            return None
        orders_string = vals.get("orders")
        order_group = json.loads(orders_string)
        return order_group.get('openERPOrders', None)
    
    @api.model
    def _get_warehouse_id(self, location, order_type_ref):
        _logger.info("\n identifying warehouse for warehouse %s, location %s", order_type_ref, location)
        if location:
            operation_types = self.env['stock.picking.type'].search([('default_location_src_id', '=', location.id)])
            if operation_types:
                mapping = self.env['order.picking.type.mapping'].search([('order_type_id', '=', order_type_ref.id),
                                                                         ('picking_type_id', 'in', operation_types.ids)],
                                                                        limit=1)
                if mapping:
                    return mapping.picking_type_id.warehouse_id
                else:
                    return operation_types[0].warehouse_id

            else:
                # either location should exist as stock location of a warehouse.
                warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', location.id)])
                if warehouse:
                    return warehouse.id
                else:
                    _logger.warning("Location is neither mapped to warehouse nor to any Operation type, "
                                    "hence sale order creation failed!")
                    # TODO: the above message seems to indicate that we should fail sale order creation,
                    #  but create_orders() seem to behave otherwise.
                    return
        else:
            _logger.warning("Location with name '%s' does not exists in the system")

       
    @api.model 
    def _get_shop_and_location_id(self, orderType, location_name, order_type_record):
        _logger.info("\n _get_shop_and_location_id().... Called.....")
        _logger.info("orderType %s",orderType)
        _logger.info("location_name %s", location_name)
        OrderTypeShopMap = self.env['order.type.shop.map']
        SaleShop = self.env['sale.shop']
        shop_list_with_order_type = None
        if location_name:
            shop_list_with_order_type = OrderTypeShopMap.search(
                [('order_type', '=', order_type_record.id), ('location_name', '=', location_name)])
            _logger.info("\nFor specified order location name [%s], shop_list_with_orderType : %s",
                         location_name, shop_list_with_order_type)
        
        if not shop_list_with_order_type:
            _logger.info("\nCouldn't identify OrderType-Shop mapping for specified order location name [%s], "
                         "searching for default OrderType-Shop map", location_name)
            shop_list_with_order_type = OrderTypeShopMap.search(
                [('order_type', '=', order_type_record.id), ('location_name', '=', None)])
            _logger.info("\nOrderType-Shop mappings without order location name specified: %s",
                         shop_list_with_order_type)

        if not shop_list_with_order_type:
            _logger.info("\nCouldn't identify OrderType-Shop mapping for Order Type [%s]", orderType)
            return False, False

        order_shop_map_object = shop_list_with_order_type[0]
        _logger.info("Identified Order Shop mapping %s", order_shop_map_object)    
        if order_shop_map_object.shop_id:
            shop_id = order_shop_map_object.shop_id.id
        else:
            shop_records = SaleShop.search([])
            first_shop = shop_records[0]
            shop_id = first_shop.id

        if order_shop_map_object.location_id:
            location_id = order_shop_map_object.location_id.id
        else:
            location_id = SaleShop.search([('id','=',shop_id)]).location_id.id

        _logger.info("\n__get_shop_and_location_id() returning shop_id: %s, location_id: %s", shop_id, location_id)
        return shop_id, location_id

    @api.model
    def create_orders(self, vals):
        customer_id = vals.get("customer_id")
        location_name = vals.get("locationName")
        all_orders = self._get_openerp_orders(vals)

        if not all_orders:
            return ""

        customer_ids = self.env['res.partner'].search([('ref', '=', customer_id)])
        if customer_ids:
            cus_id = customer_ids[0]

            for orderType, ordersGroup in groupby(all_orders, lambda order: order.get('type')):

                order_type_def = self.env['order.type'].search([('name','=',orderType)])
                if (not order_type_def):
                    _logger.info("\nOrder Type is not defined. Ignoring %s for Customer %s",orderType,cus_id)
                    continue

                orders = list(ordersGroup)
                care_setting = orders[0].get('visitType').lower()
                provider_name = orders[0].get('providerName')
                # will return order line data for products which exists in the system, either with productID passed
                # or with conceptName
                unprocessed_orders = self._filter_processed_orders(orders)
                _logger.info("\n DEBUG: Unprocessed Orders: %s", unprocessed_orders)
                shop_id, location_id = self._get_shop_and_location_id(orderType, location_name, order_type_def)
                # shop_id = tup[0]
                # location_id = tup[1]

                if (not shop_id):
                    err_message = "Can not process order. Order type:{} - should be matched to a shop".format(orderType)
                    _logger.info(err_message)
                    raise Warning(err_message)
                    
                
                shop_obj = self.env['sale.shop'].search([('id','=',shop_id)])
                warehouse_id = shop_obj.warehouse_id.id
                _logger.warning("warehouse_id: %s"%(warehouse_id))

                name = self.env['ir.sequence'].next_by_code('sale.order')
                #Adding both the ids to the unprocessed array of orders, Separating to dispensed and non-dispensed orders
                unprocessed_dispensed_order = []
                unprocessed_non_dispensed_order = []
                for unprocessed_order in unprocessed_orders:
                    unprocessed_order['location_id'] = location_id
                    unprocessed_order['warehouse_id'] = warehouse_id
                    if(unprocessed_order.get('dispensed', 'false') == 'true'):
                        unprocessed_dispensed_order.append(unprocessed_order)
                    else:
                        unprocessed_non_dispensed_order.append(unprocessed_order)

                if(len(unprocessed_non_dispensed_order) > 0):
                    _logger.debug("\n Processing Unprocessed non dispensed Orders: %s", list(unprocessed_non_dispensed_order))
                    sale_order_ids = self.env['sale.order'].search([('partner_id', '=', cus_id.id),
                                                                    ('shop_id', '=', shop_id),
                                                                    ('state', '=', 'draft'),
                                                                    ('origin', '=', 'ATOMFEED SYNC')])
                    if(not sale_order_ids):
                        # Non Dispensed New
                        # replaced create_sale_order method call
                        _logger.debug("\n No existing sale order for Unprocessed non dispensed Orders. Creating .. ")
                        sale_order_vals = {'partner_id': cus_id.id,
                                           'location_id': unprocessed_non_dispensed_order[0]['location_id'],
                                           'warehouse_id': unprocessed_non_dispensed_order[0]['warehouse_id'],
                                           'care_setting': care_setting,
                                           'provider_name': provider_name,
                                           'date_order': datetime.strftime(datetime.now(), DTF),
                                           'pricelist_id': cus_id.property_product_pricelist and cus_id.property_product_pricelist.id or False,
                                           'payment_term_id': shop_obj.payment_default_id.id,
                                           'project_id': shop_obj.project_id.id if shop_obj.project_id else False,
                                           'picking_policy': 'direct',
                                           'state': 'draft',
                                           'shop_id': shop_id,
                                           'origin': 'ATOMFEED SYNC',
                                           }
                        if shop_obj.pricelist_id:
                            sale_order_vals.update({'pricelist_id': shop_obj.pricelist_id.id})
                        sale_order = self.env['sale.order'].create(sale_order_vals)
                        _logger.debug("\n Created a new Sale Order for non dispensed orders. ID: %s. Processing order lines ..", sale_order.id)
                        for rec in unprocessed_non_dispensed_order:
                            self._process_orders(sale_order, unprocessed_non_dispensed_order, rec)
                    else:
                        # Non Dispensed Update
                        # replaced update_sale_order method call
                        for order in sale_order_ids:
                            order.write({'care_setting': care_setting, 'provider_name': provider_name})
                            for rec in unprocessed_non_dispensed_order:
                                self._process_orders(order, unprocessed_non_dispensed_order, rec)
                            # break from the outer loop
                            break

                    # sale_order_ids_for_dispensed = self.env['sale.order'].search([('partner_id', '=', cus_id.id),
                    #                                                               ('shop_id', '=', shop_id),
                    #                                                               ('state', '=', 'draft'),
                    #                                                               ('origin', '=', 'ATOMFEED SYNC')])
                    #
                    # if (len(sale_order_ids_for_dispensed) > 0):
                    #     if (sale_order_ids_for_dispensed[0]):
                    #         sale_order_line_ids_for_dispensed = self.env['sale.order.line'].search(
                    #             [('order_id', '=', sale_order_ids_for_dispensed[0])])
                    #         if (len(sale_order_line_ids_for_dispensed) != 0):
                    #             for so_ids in sale_order_line_ids_for_dispensed:
                    #                 so_ids.unlink()

                if (len(unprocessed_dispensed_order) > 0):
                    _logger.debug("\n Processing Unprocessed dispensed Orders: %s", list(unprocessed_dispensed_order))
                    auto_convert_dispensed = self.env['ir.values'].search([('model', '=', 'sale.config.settings'),
                                                                           ('name', '=', 'convert_dispensed')]).value
                    auto_invoice_dispensed = self.env.ref('bahmni_sale.auto_register_invoice_payment_for_dispensed').value


                    sale_order_ids = self.env['sale.order'].search([('partner_id', '=', cus_id.id),
                                                                    ('shop_id', '=', shop_id),
                                                                    ('state', '=', 'draft'),
                                                                    ('origin', '=', 'ATOMFEED SYNC')])

                    if any(sale_order_ids):
                        _logger.debug("\n For exsiting sale orders for the shop, trying to unlink any openmrs order if any")
                        self._unlink_sale_order_lines_and_remove_empty_orders(sale_order_ids,unprocessed_dispensed_order)

                    sale_order_ids_for_dispensed = self.env['sale.order'].search([('partner_id', '=', cus_id.id),
                                                                                  ('shop_id', '=', shop_id),
                                                                                  ('location_id', '=', location_id),
                                                                                  ('state', '=', 'draft'),
                                                                                  ('origin', '=', 'ATOMFEED SYNC')])

                    if not sale_order_ids_for_dispensed:
                        _logger.debug("\n Could not find any sale_order at specified shop and stock location. Creating a new Sale order for dispensed orders")

                        # TODO: commenting off anand's code for now
                        # dispensed = False
                        # for order in unprocessed_dispensed_order:
                        #     for line in sale_order_line_ids:
                        #         if order.get('orderId') == line.external_order_id and order.get('dispensed')!='false':
                        #             line.write({'dispensed':True})
                        #             dispensed = True
                        # if dispensed:
                        #     auto_convert_set = self.env['ir.values'].search([('model', '=', 'sale.config.settings'),
                        #                              ('name', '=', 'convert_dispensed')]).value
                        #     if auto_convert_set:
                        #         sale_order_ids.action_confirm()
                        #         sale_order_ids.validate_payment()

                        sale_order_dict = {'partner_id': cus_id.id,
                                           'location_id': location_id,
                                           'warehouse_id': warehouse_id,
                                           'care_setting': care_setting,
                                           'provider_name': provider_name,
                                           'date_order': datetime.strftime(datetime.now(), DTF),
                                           'pricelist_id': cus_id.property_product_pricelist and cus_id.property_product_pricelist.id or False,
                                           'payment_term_id': shop_obj.payment_default_id.id,
                                           'project_id': shop_obj.project_id.id if shop_obj.project_id else False,
                                           'picking_policy': 'direct',
                                           'state': 'draft',
                                           'shop_id': shop_id,
                                           'origin': 'ATOMFEED SYNC'}
                        if shop_obj.pricelist_id:
                            sale_order_dict.update({'pricelist_id': shop_obj.pricelist_id.id})
                        new_sale_order = self.env['sale.order'].create(sale_order_dict)
                        _logger.debug("\n Created a new Sale Order. ID: %s. Processing order lines ..", new_sale_order.id)
                        for line in unprocessed_dispensed_order:
                            self._process_orders(new_sale_order, unprocessed_dispensed_order, line)

                        if auto_convert_dispensed:
                            _logger.debug("\n Confirming delivery and payment for the newly created sale order..")
                            new_sale_order.auto_validate_delivery()
                            if auto_invoice_dispensed == '1':
                                new_sale_order.validate_payment()

                    else:
                        _logger.debug("\n There are other sale_orders at specified shop and stock location.")
                        sale_order_to_process = None
                        if not auto_convert_dispensed:
                            # try to find an existing sale order to add the openmrs orders to
                            if any(sale_order_ids_for_dispensed):
                                _logger.debug("\n Found a sale order to append dispensed lines. ID : %s",sale_order_ids_for_dispensed[0].id)
                                sale_order_to_process = sale_order_ids_for_dispensed[0]

                        if not sale_order_to_process:
                            # create new sale order
                            _logger.debug("\n Post unlinking of order lines. Could not find  a sale order to append dispensed lines. Creating .. ")
                            sales_order_obj = {'partner_id': cus_id.id,
                                               'location_id': location_id,
                                               'warehouse_id': warehouse_id,
                                               'care_setting': care_setting,
                                               'provider_name': provider_name,
                                               'date_order': datetime.strftime(datetime.now(), DTF),
                                               'pricelist_id': cus_id.property_product_pricelist and cus_id.property_product_pricelist.id or False,
                                               'payment_term_id': shop_obj.payment_default_id.id,
                                               'project_id': shop_obj.project_id.id if shop_obj.project_id else False,
                                               'picking_policy': 'direct',
                                               'state': 'draft',
                                               'shop_id': shop_id,
                                               'origin': 'ATOMFEED SYNC'}

                            if shop_obj.pricelist_id:
                                sales_order_obj.update({'pricelist_id': shop_obj.pricelist_id.id})
                            sale_order_to_process = self.env['sale.order'].create(sales_order_obj)
                            _logger.info("\n DEBUG: Created a new Sale Order. ID: %s", sale_order_to_process.id)

                        _logger.debug("\n Processing dispensed lines. Appending to Order ID %s", sale_order_to_process.id)
                        for line in unprocessed_dispensed_order:
                            self._process_orders(sale_order_to_process, unprocessed_dispensed_order, line)

                        if auto_convert_dispensed and sale_order_to_process:
                            _logger.debug("\n Confirming delivery and payment ..")
                            sale_order_to_process.auto_validate_delivery()
                            # TODO: payment validation checks
                            # TODO: 1) Should be done through a config "sale.config.settings"[auto_invoice_dispensed]"
                            # TODO: 2) Should check the invoice amount. Odoo fails/throws-error if the invoice amount is 0.
                            if auto_invoice_dispensed == '1':
                                sale_order_to_process.validate_payment()

        else:
            raise Warning("Patient Id not found in Odoo")

    @api.model
    def _remove_existing_sale_order_line(self, sale_order_id, unprocessed_dispensed_order):
        sale_order_lines = self.env['sale.order.line'].search([('order_id', '=', sale_order_id.id)])
        sale_order_lines_to_be_saved = []
        sale_order_lines_unliked = []
        for order in unprocessed_dispensed_order:
            for sale_order_line in sale_order_lines:
                if(order['orderId'] == sale_order_line.external_order_id):
                    if order.get('dispensed')=='false':
                        dispensed = False
                    else:
                        dispensed = True
                    if(dispensed != sale_order_line.dispensed):
                        sale_order_lines_to_be_saved.append(sale_order_line)

        for rec in sale_order_lines_to_be_saved:
            sale_order_lines_unliked.append(rec.id)
            rec.unlink()

        return sale_order_lines_unliked

        
    @api.model
    def _process_orders(self, sale_order, all_orders, order):
        external_order_id = order['orderId']
        order_dispensed = order.get('dispensed', ORDER_DISPENSED_FALSE)
        # order_in_db = self.env['sale.order.line'].search([('external_order_id', '=', external_order_id)])
        # if(order_in_db or self._order_already_processed(external_order_id, order_dispensed)):
        #     return
        if self._order_already_processed(external_order_id, order_dispensed):
            return

        parent_order_line = []
        # if(order.get('previousOrderId', False) and order.get('dispensed', "") == "true"):
        #     self._create_sale_order_line(cr, uid, name, sale_order, order, context)

        if order.get('previousOrderId', False) and order_dispensed == 'false':
            parent_order = self._fetch_parent(all_orders, order)
            if(parent_order):
                self._process_orders(sale_order, all_orders, parent_order)
            parent_order_line = self.env['sale.order.line'].search([('external_order_id', '=', order['previousOrderId'])])
            if(not parent_order_line and not self._order_already_processed(order['previousOrderId'], order_dispensed)):
                raise Warning("Previous order id does not exist in DB. This can be because of previous failed events")

        if(order["voided"] or order.get('action', "") == "DISCONTINUE"):
            self._delete_sale_order_line(parent_order_line)
        elif(order.get('action', "") == "REVISE" and order_dispensed == "false"):
            self._update_sale_order_line(sale_order.id, order, parent_order_line)
        else:
            self._create_sale_order_line(sale_order.id, order)
    
    @api.model
    def _delete_sale_order_line(self, parent_order_line):
        if(parent_order_line):
            if(parent_order_line[0] and parent_order_line[0].order_id.state == 'draft'):
                for parent in parent_order_line:
                    parent.unlink()
    
    @api.model
    def _update_sale_order_line(self, sale_order, order, parent_order_line):
        self._delete_sale_order_line(parent_order_line)
        self._create_sale_order_line(sale_order, order)
    
    @api.model
    def _create_sale_order_line(self, sale_order, order):
        if self._order_already_processed(order['orderId'], order.get('dispensed', ORDER_DISPENSED_FALSE)):
            return
        self._create_sale_order_line_function(sale_order, order)
        
    @api.model
    def _get_order_quantity(self, order, default_quantity_value):
        if(not self.env['syncable.units'].search([('name', '=', order['quantityUnits'])])):
            return default_quantity_value
        return order['quantity']
    
    @api.model
    def _create_sale_order_line_function(self, sale_order, order):
        stored_prod_ids = self._get_product_ids(order)

        if(stored_prod_ids):
            prod_id = stored_prod_ids[0]
            prod_obj = self.env['product.product'].browse(prod_id)
            sale_order_line_obj = self.env['sale.order.line']
            prod_lot = sale_order_line_obj.get_available_batch_details(prod_id, sale_order)

            actual_quantity = order['quantity']
            comments = " ".join([str(actual_quantity), str(order.get('quantityUnits', None))])

            default_quantity_total = self.env.ref('bahmni_sale.group_default_quantity')
            _logger.info("DEFAULT QUANTITY TOTAL")
            _logger.info(default_quantity_total)
            default_quantity_value = 1
            if default_quantity_total and len(default_quantity_total.users) > 0:
                default_quantity_value = -1

            order['quantity'] = self._get_order_quantity(order, default_quantity_value)
            product_uom_qty = order['quantity']
            if(prod_lot != None and order['quantity'] > prod_lot.stock_forecast):
                product_uom_qty = prod_lot.stock_forecast

            order_line_dispensed = True if order.get('dispensed') == 'true' or (order.get('dispensed') and order.get('dispensed') != 'false') else False
            sale_order_line = {
                'product_id': prod_id,
                'price_unit': prod_obj.list_price,
                'comments': comments,
                'product_uom_qty': product_uom_qty,
                'product_uom': prod_obj.uom_id.id,
                'order_id': sale_order,
                'external_id':order['encounterId'],
                'external_order_id':order['orderId'],
                'name': prod_obj.name,
                'type': 'make_to_stock',
                'state': 'draft',
                'dispensed': order_line_dispensed
            }

            if prod_lot != None:
                life_date = prod_lot.life_date and datetime.strptime(prod_lot.life_date, DTF)
                if self.env.ref('bahmni_sale.sale_price_basedon_cost_price_markup').value == '1':
                    sale_order_line['price_unit'] = prod_lot.sale_price if prod_lot.sale_price > 0.0 else sale_order_line['price_unit']
                sale_order_line['batch_name'] = prod_lot.name
                sale_order_line['batch_id'] = prod_lot.id
                sale_order_line['expiry_date'] = life_date and life_date.strftime(DTF)
            
            
            sale_obj = self.env['sale.order'].browse(sale_order)
            sale_line = sale_order_line_obj.create(sale_order_line)
            
            sale_line._compute_tax_id()
            if sale_obj.pricelist_id:
                line_product = prod_obj.with_context(
                    lang = sale_obj.partner_id.lang,
                    partner = sale_obj.partner_id.id,
                    quantity = sale_line.product_uom_qty,
                    date = sale_obj.date_order,
                    pricelist = sale_obj.pricelist_id.id,
                    uom = prod_obj.uom_id.id
                )
                price = self.env['account.tax']._fix_tax_included_price_company(sale_line._get_display_price(prod_obj), prod_obj.taxes_id, sale_line.tax_id, sale_line.company_id)
                sale_line.price_unit = price

            if product_uom_qty != order['quantity']:
                order['quantity'] = order['quantity'] - product_uom_qty
                self._create_sale_order_line_function(sale_order, order)
    
    def _fetch_parent(self, all_orders, child_order):
        for order in all_orders:
            if(order.get("orderId") == child_order.get("previousOrderId")):
                return order

    @api.model
    def _is_order_revised_processed(self, all_orders, order_to_process):
        parent_order_line = None
        for order in all_orders:
            if order.get('previousOrderId', '') == order_to_process.get('orderId'):
                parent_order_line = self.env['sale.order.line'].search([('external_order_id', '=', order.get('orderId'))])
                break
        return True if parent_order_line and any(parent_order_line) else False

    @api.model
    def _filter_processed_orders(self, orders):
        unprocessed_orders = []
        # sort the orders so that the revised ones appear later
        orders.sort(key=lambda order_item: 1 if order_item.get('previousOrderId', '') == '' else 2)
        for order in orders:
            if self._is_order_revised_processed(orders, order):
                continue
            dispensed_status = order.get('dispensed') == 'true'
            existing_order_line = self.env['sale.order.line'].search([('external_order_id', '=', order['orderId'])])
            if not existing_order_line:
                unprocessed_orders.append(order)
            else:
                sale_order_line = existing_order_line[0]
                if not sale_order_line.dispensed and dispensed_status:
                    unprocessed_orders.append(order)

            # sale_order_line = self.env['sale.order.line'].search([('external_order_id', '=', order['orderId']), ('dispensed', '=', False)])
            # if not sale_order_line:
            #     unprocessed_orders.append(order)
        return self._filter_products_undefined(unprocessed_orders)

    @api.model
    def _order_already_processed(self, external_order_id, dispensed_status):
        dispensed = True if dispensed_status == 'true' else False
        existing_order_line = self.env['sale.order.line'].search([('external_order_id', '=', external_order_id)])
        if not existing_order_line:
            return False
        elif any(existing_order_line):
            sale_order = self.env['sale.order'].search([('id', '=', existing_order_line[0].order_id.id)])
            _logger.info("\n Checking for order line's parent Order state")
            if sale_order[0].state != 'draft':
                return True
            return existing_order_line[0].dispensed == dispensed
        else:
            return False


    @api.model
    def _filter_products_undefined(self, orders):
        products_in_system = []

        for order in orders:
            stored_prod_ids = self._get_product_ids(order)
            if(stored_prod_ids):
                products_in_system.append(order)
        return products_in_system

    @api.model
    def _get_product_ids(self, order):
        if order['productId']:
            prod_ids = self.env['product.product'].search([('uuid', '=', order['productId'])])
        else:
            prod_ids = self.env['product.product'].search([('name', '=', order['conceptName'])])
        return prod_ids.ids


    @api.model
    def _unlink_sale_order_lines_and_remove_empty_orders(self, sale_orders, openmrs_orders):
        for existing_sale_order in sale_orders:
            _logger.info("\n DEBUG: checking existing sale order for any older order_lines. ID : %s", existing_sale_order.id)
            # Remove existing sale order line
            if not any(self._remove_existing_sale_order_line(existing_sale_order, openmrs_orders)):
                continue
            # Removing existing empty sale order
            exisiting_sale_order_lines = self.env['sale.order.line'].search([('order_id', '=', existing_sale_order.id)])
            if not exisiting_sale_order_lines or not any(exisiting_sale_order_lines):
                _logger.info("\n DEBUG: Removing Empty Sale Order. ID : %s", existing_sale_order.id)
                existing_sale_order.unlink()
