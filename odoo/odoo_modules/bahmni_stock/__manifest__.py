# -*- coding: utf-8 -*-
{
    'name': 'Bahmni Stock',
    'version': '1.0',
    'summary': 'Custom stock module to meet bahmni requirement',
    'sequence': 1,
    'description': """
Bahmni Purchase
====================
""",
    'category': 'Stock',
    'website': '',
    'images': [],
    'depends': ['stock', 'bahmni_product', 'bahmni_account'],
    'data': ['views/stock_production_lot_view.xml',
             'views/stock_picking_view.xml',
             'views/stock_pack_operation_view.xml',
             'views/account_invoice_line.xml',
             'views/account_payment_view.xml',
             'report/batch_stock_future_forecast_view.xml',
             'report/stock_report_prod_by_last_moved.xml',
             'report/account_payment_report.xml',
             'views/bahmni_stock_report_mapping.xml',
             'security/ir.model.access.csv',
             ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
