# -*- coding: utf-8 -*-
from datetime import datetime, date
from lxml import etree

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.osv.orm import setup_modifiers
from odoo.tools import pickle
import logging
_logger = logging.getLogger(__name__)



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total', 'discount', 'chargeable_amount')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            amount_total = amount_untaxed + amount_tax
            if order.chargeable_amount > 0.0:
                discount = amount_total - order.chargeable_amount
            else:
                discount = order.discount
            amount_total = amount_total - discount
            round_off_amount = self.env['rounding.off'].round_off_value_to_nearest(amount_total)
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_total + round_off_amount,
                'round_off_amount': round_off_amount,
                'total_outstanding_balance': order.prev_outstanding_balance + amount_total + round_off_amount
            })

    @api.depends('partner_id')
    def _calculate_balance(self):
        for order in self:
            order.prev_outstanding_balance = 0.0
            order.total_outstanding_balance = 0.0
            total_receivable = order._total_receivable()
            order.prev_outstanding_balance = total_receivable
    
    def _total_receivable(self):
        receivable = 0.0
        if self.partner_id:
            self._cr.execute("""SELECT l.partner_id, at.type, SUM(l.debit-l.credit)
                          FROM account_move_line l
                          LEFT JOIN account_account a ON (l.account_id=a.id)
                          LEFT JOIN account_account_type at ON (a.user_type_id=at.id)
                          WHERE at.type IN ('receivable','payable')
                          AND l.partner_id = %s
                          AND l.full_reconcile_id IS NULL
                          GROUP BY l.partner_id, at.type
                          """, (self.partner_id.id,))
            for pid, type, val in self._cr.fetchall():
                if val is None:
                    val=0
                receivable = (type == 'receivable') and val or -val
        return receivable

    @api.depends('partner_id')
    def _get_partner_details(self):
        for order in self:
            partner = order.partner_id
            order.update({
                'partner_uuid': partner.uuid,
                #'partner_village': partner.village,
            })


    partner_village = fields.Many2one("village.village", string="Partner Village")
    care_setting = fields.Selection([('ipd', 'IPD'),
                                     ('opd', 'OPD')], string="Care Setting")
    provider_name = fields.Char(string="Provider Name")
    discount_percentage = fields.Float(string="Discount Percentage")
    default_quantity = fields.Integer(string="Default Quantity")
    # above field is used to allow setting quantity as -1 in sale order line, when it is created through bahmni
    discount_type = fields.Selection([('none', 'No Discount'),
                                      ('fixed', 'Fixed'),
                                      ('percentage', 'Percentage')], string="Discount Type",
                                     default='none')
    discount = fields.Monetary(string="Discount")
    disc_acc_id = fields.Many2one('account.account', string="Discount Account Head")
    round_off_amount = fields.Float(string="Round Off Amount", compute=_amount_all)
    prev_outstanding_balance = fields.Monetary(string="Previous Outstanding Balance",
                                               compute=_calculate_balance)
    total_outstanding_balance = fields.Monetary(string="Total Outstanding Balance",
                                                compute=_amount_all)
    chargeable_amount = fields.Float(string="Chargeable Amount")
    amount_round_off = fields.Float(string="Round Off Amount")
    # location to identify from which location order is placed.
    location_id = fields.Many2one('stock.location', string="Location")
    partner_uuid = fields.Char(string='Customer UUID', store=True, readonly=True, compute='_get_partner_details')
    shop_id = fields.Many2one('sale.shop', 'Shop', required=True)


    @api.onchange('order_line')
    def onchange_order_line(self):
        '''Calculate discount amount, when discount is entered in terms of %'''
        amount_total = self.amount_untaxed + self.amount_tax
        if self.discount_type == 'fixed':
            self.discount_percentage = self.discount/amount_total * 100
        elif self.discount_type == 'percentage':
            self.discount = amount_total * self.discount_percentage / 100

    @api.onchange('discount', 'discount_percentage', 'discount_type', 'chargeable_amount')
    def onchange_discount(self):
        amount_total = self.amount_untaxed + self.amount_tax
        if self.chargeable_amount:
            if self.discount_type == 'none' and self.chargeable_amount:
                self.discount_type = 'fixed'
                discount = amount_total - self.chargeable_amount
                self.discount_percentage = (discount / amount_total) * 100
        else:
            if self.discount:
                self.discount_percentage = (self.discount / amount_total) * 100
            if self.discount_percentage:
                self.discount = amount_total * self.discount_percentage / 100

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''1. make percentage and discount field readonly, when chargeable amount is allowed to enter'''
        result = super(SaleOrder, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            group_id = self.env.ref("bahmni_sale.group_allow_change_so_charge").id
            doc = etree.XML(result['arch'])
            if group_id in self.env.user.groups_id.ids:
                for node in doc.xpath("//field[@name='discount_percentage']"):
                    node.set('readonly', '1')
                    setup_modifiers(node, result['fields']['discount_percentage'])
                for node in doc.xpath("//field[@name='discount']"):
                    node.set('readonly', '1')
                    setup_modifiers(node, result['fields']['discount'])
                for node in doc.xpath("//field[@name='discount_type']"):
                    node.set('readonly', '1')
                    setup_modifiers(node, result['fields']['discount_type'])
            result['arch'] = etree.tostring(doc)
        return result

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'discount_type': self.discount_type,
            'discount_percentage': self.discount_percentage,
            'disc_acc_id': self.disc_acc_id.id,
            'discount': self.discount,
        }
        return invoice_vals


    #By Pass the Invoice wizard while we press the "Create Invoice" button in sale order afer confirmation.
    #So Once we Confirm the sale order it will create the invoice and ask for the register payment.
    @api.multi
    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        self.validate_delivery()
        #here we need to set condition for if the its enabled then can continuw owise return True in else condition
        if self.env.user.has_group('bahmni_sale.group_skip_invoice_options'):
            for order in self:
                inv_data = order._prepare_invoice()
                created_invoice = self.env['account.invoice'].create(inv_data)

                for line in order.order_line:
                    line.invoice_line_create(created_invoice.id, line.product_uom_qty)

                # Use additional field helper function (for account extensions)
                for line in created_invoice.invoice_line_ids:
                    line._set_additional_fields(created_invoice)

                # Necessary to force computation of taxes. In account_invoice, they are triggered
                # by onchanges, which are not triggered when doing a create.
                created_invoice.compute_taxes()
                created_invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': created_invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
                created_invoice.action_invoice_open()#Validate Invoice
                ctx = dict(
                default_invoice_ids = [(4, created_invoice.id, None)]
                )
                reg_pay_form = self.env.ref('account.view_account_payment_invoice_form')
                return {
                    'name': _('Register Payment'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.payment',
                    'views': [(reg_pay_form.id, 'form')],
                    'view_id': reg_pay_form.id,
                    'target': 'new',
                    'context': ctx,
                }
        else:
            return res


    #This method will be called when validation is happens from the Bahmni side
    @api.multi
    def auto_validate_delivery(self):
        super(SaleOrder, self).action_confirm()
        self.validate_delivery()

    @api.multi
    def validate_delivery(self):
        if self.env.ref('bahmni_sale.validate_delivery_when_order_confirmed').value == '1':
            allow_negative = self.env.ref('bahmni_sale.allow_negative_stock')
            if self.picking_ids:
                for picking in self.picking_ids:
                    if picking.state in ('waiting','confirmed','partially_available') and allow_negative.value == '1':
                        picking.force_assign()#Force Available
                    found_issue = False
                    if picking.state not in ('waiting','confirmed','partially_available'):
                        for pack in picking.pack_operation_product_ids:
                            if pack.product_id.tracking != 'none':
                                line = self.order_line.filtered(lambda l:l.product_id == pack.product_id)
                                lot_ids = None
                                if line.lot_id:
                                    lot_ids = line.lot_id
                                else:
                                    lot_ids = self._find_batch(pack.product_id,pack.product_qty,pack.location_id,picking)
                                if lot_ids:
                                    #First need to Find the related move_id of this operation
                                    operation_link_obj = self.env['stock.move.operation.link'].search([('operation_id','=',pack.id)],limit=1)
                                    move_obj = operation_link_obj.move_id
                                    #Now we have to update entry to the related table which holds the lot, stock_move and operation entrys
                                    pack_operation_lot = self.env['stock.pack.operation.lot'].search([('operation_id','=',pack.id)],limit=1)
                                    for lot in lot_ids:
                                        pack_operation_lot.write({
                                            'lot_name': lot.name,
                                            'qty': pack.product_qty,
                                            'operation_id': pack.id,
                                            'move_id': move_obj.id,
                                            'lot_id': lot.id,
                                            'cost_price': lot.cost_price,
                                            'sale_price': lot.sale_price,
                                            'mrp': lot.mrp
                                            })
                                    pack.qty_done = pack.product_qty
                                else:
                                    found_issue = True
                            else:
                                pack.qty_done = pack.product_qty
                        if not found_issue:
                            picking.do_new_transfer()#Validate
                    else:
                        message = ("<b>Auto validation Failed</b> <br/> <b>Reason:</b> There are not enough stock available for Some product on <a href=# data-oe-model=stock.location data-oe-id=%d>%s</a> Location") % (self.location_id,self.location_id.name)
                        self.message_post(body=message)

    def _find_batch(self, product, qty, location, picking):
        _logger.info("\n\n***** Product :%s, Quantity :%s Location :%s\n*****",product,qty,location)
        lot_objs = self.env['stock.production.lot'].search([('product_id','=',product.id),('life_date','>=',str(fields.datetime.now()))])
        _logger.info('\n *** Searched Lot Objects:%s \n',lot_objs)
        if any(lot_objs):
            #Sort losts based on the expiry date FEFO(First Expiry First Out)
            lot_objs = list(lot_objs)
            sorted_lot_list = sorted(lot_objs, key=lambda l: l.life_date)
            _logger.info('\n *** Sorted based on FEFO :%s \n',sorted_lot_list)
            done_qty = qty
            res_lot_ids = []
            lot_ids_for_query = tuple([lot.id for lot in sorted_lot_list])
            self._cr.execute("SELECT SUM(qty) FROM stock_quant WHERE lot_id IN %s and location_id=%s",(lot_ids_for_query,location.id,))
            qry_rslt = self._cr.fetchall()
            available_qty = qry_rslt[0] and qry_rslt[0][0] or 0
            if available_qty >= qty:
                for lot_obj in sorted_lot_list:
                    quants = lot_obj.quant_ids.filtered(lambda q: q.location_id == location)
                    for quant in quants:
                        if done_qty >= 0:
                            res_lot_ids.append(lot_obj)
                            done_qty = done_qty - quant.qty
                return res_lot_ids
            else:
                message = ("<b>Auto validation Failed</b> <br/> <b>Reason:</b> There are not enough stock available for <a href=# data-oe-model=product.product data-oe-id=%d>%s</a> product on <a href=# data-oe-model=stock.location data-oe-id=%d>%s</a> Location") % (product.id,product.name,location.id,location.name)
                self.message_post(body=message)
        else:
            message = ("<b>Auto validation Failed</b> <br/> <b>Reason:</b> There are no Batches/Serial no's available for <a href=# data-oe-model=product.product data-oe-id=%d>%s</a> product") % (product.id,product.name)
            self.message_post(body=message)
            return False
       
    @api.onchange('shop_id')
    def onchange_shop_id(self):
        self.warehouse_id = self.shop_id.warehouse_id.id
        self.location_id = self.shop_id.location_id.id
        self.payment_term_id = self.shop_id.payment_default_id.id
        self.project_id = self.shop_id.project_id.id if self.shop_id.project_id else False
        if self.shop_id.pricelist_id:
            self.pricelist_id = self.shop_id.pricelist_id.id
            
    @api.multi
    def validate_payment(self):
        for obj in self:
            ctx = {'active_ids': [obj.id]}
            default_vals = self.env['sale.advance.payment.inv'
                                        ].with_context(ctx).default_get(['count', 'deposit_taxes_id',
                                                                         'advance_payment_method', 'product_id',
                                                                         'deposit_account_id'])
            payment_inv_wiz = self.env['sale.advance.payment.inv'].with_context(ctx).create(default_vals)
            payment_inv_wiz.with_context(ctx).create_invoices()
            for inv in obj.invoice_ids:
                inv.action_invoice_open()
                if inv.state == 'paid':
                    continue
                elif inv.amount_total > 0:
                    account_payment_env = self.env['account.payment']
                    fields = account_payment_env.fields_get().keys()
                    default_fields = account_payment_env.with_context({'default_invoice_ids': [(4, inv.id, None)]}).default_get(fields)
                    journal_id = self.env['account.journal'].search([('type', '=', 'cash')],
                                                                    limit=1)
                    default_fields.update({'journal_id': journal_id.id})
                    payment_method_ids = self.env['account.payment.method'
                                                  ].search([('payment_type', '=', default_fields.get('payment_type'))]).ids
                    if default_fields.get('payment_type') == 'inbound':
                        journal_payment_methods = journal_id.inbound_payment_method_ids.ids
                    elif default_fields.get('payment_type') == 'outbound':
                        journal_payment_methods = journal_id.outbound_payment_method_ids.ids
                    common_payment_method = list(set(payment_method_ids).intersection(set(journal_payment_methods)))
                    common_payment_method.sort()
                    default_fields.update({'payment_method_id': common_payment_method[0]})
                    account_payment = account_payment_env.create(default_fields)
                    account_payment.post()
                else:
                    message = "<b>Auto validation Failed</b> <br/> <b>Reason:</b> The Total amount is 0 So, Can't Register Payment."
                    inv.message_post(body=message)

