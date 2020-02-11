# -*- coding: utf-8 -*-
import base64
import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.addons.web.controllers.main import CSVExport
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF


class StockLocationProductDhis2(models.TransientModel):
    _name = 'stock.location.product.dhis2'
    _description = "DHIS2 Export product stock at location"

    MONTHS = [(1, "Jan"), (2, "Feb"), (3, "Mar"), (4, "Apr"), (5, "May"),
              (6, "Jun"), (7, "Jul"),
              (8, "Aug"), (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dec")]

    FIELDS = ['dhis2_code', 'virtual_available']
    HEADERS = ['dataelement', 'period', 'orgunit', 'categoryoptioncombo',
               'value', 'storedby', 'lastupdated', 'comment', 'followup']

    @api.model
    def _get_available_years_in_system(self):
        '''this method will return selection values for the years,
        for which entries are available in the system'''
        res = []
        date_today = datetime.date.today()
        start_date_stock_move = self.env['stock.move'].search([], order='date asc', limit=1).date
        if start_date_stock_move:
            start_date_stock_move = datetime.datetime.strptime(start_date_stock_move, DTF).date()
        start_date_account_move = self.env['account.move'].search([], order='date asc', limit=1).date
        if start_date_account_move:
            start_date_account_move = datetime.datetime.strptime(start_date_account_move, DF).date()
        if start_date_account_move and start_date_stock_move:
            start_year = False
            if start_date_stock_move < start_date_account_move:
                start_year = start_date_stock_move.year
            else:
                start_year = start_date_account_move.year
            if (str(start_year), start_year) not in res:
                res.append((str(start_year), start_year))
            if date_today.year > start_year:
                for i in range(start_year, date_today.year):
                    if (str(i+1), i+1) not in res:
                        res.append((str(i+1), i+1))
        else:
            if start_date_account_move:
                res.append((str(start_date_account_move.year), start_date_account_move.year))
            elif start_date_stock_move:
                res.append((str(start_date_stock_move.year), start_date_stock_move.year))
            else:
                res.append((str(date_today.year), date_today.year))
        return res

    from_date = fields.Datetime(string="From Date")
    to_date = fields.Datetime(string="To Date")
    month = fields.Selection(MONTHS, string="Month")
    year = fields.Selection(_get_available_years_in_system, string='Year')
    data = fields.Binary(string="CSV file")
    data_fname = fields.Char(string="File Name", default="stock_product_location.csv")
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             string="State", default="choose")

    @api.multi
    def action_generate_csv(self):
        self.ensure_one()
        dialog_box_data = self.read(['month', 'year', 'to_date', 'from_date'])[0]
        export_data = self._get_export_data(dialog_box_data)
        csv_data = CSVExport().from_data(self.HEADERS, export_data)
 
        self.write({'data': base64.encodestring(csv_data),
                    'state': 'get'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.location.product.dhis2',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.model
    def _get_export_data(self, dialog_box_data):
        product_model = self.env['product.product']
        domain = [('type', '<>', 'service')]
        product_search_context = self.with_context(self._context)._create_product_search_context(dialog_box_data)
        product_obj = product_model.with_context(product_search_context).search(domain)

        export_data = product_obj.export_data(self.FIELDS).get('datas', [])
        company = self.env['res.company'].browse(self._context.get('active_id'))
        orgunit = company.dhis2_code
        period = datetime.date(year=int(dialog_box_data['year']), month=int(dialog_box_data['month']), day=1).strftime("%Y%m")
        modified_export_data = []
        for row in export_data:
            modified_row = []
            modified_row.append(row[0])  #dataelement
            modified_row.append(period)
            modified_row.append(orgunit)
            modified_row.append(None)   #categoryoptioncombo
            modified_row.append(row[1]) #value
            modified_row.append(None)   #storedby
            modified_row.append(None)   #lastupdated
            modified_row.append(None)   #comment
            modified_row.append(None)   #followup
            modified_export_data.append(modified_row)
        return modified_export_data

    def _create_product_search_context(self, data):
        first_day_of_month = datetime.date(year=int(data['year']), month=int(data['month']), day=1)
        first_day_of_next_month = first_day_of_month + relativedelta(months=1)
        return {
            'from_date': data['from_date'],
            'to_date': datetime.datetime.strftime(first_day_of_next_month, DF),
        }
