# -*- coding: utf-8 -*-
{
    'name': 'Bahmni Atom Feed',
    'version': '1.0',
    'summary': 'Module to sync Bahmni with Odoo',
    'sequence': 1,
    'description': """
Bahmni Web Extension
====================
""",
    'category': 'Web',
    'website': '',
    'images': [],
    'depends': ['web', 'bahmni_product', 'bahmni_sale'],
    'data': ['security/ir.model.access.csv',
         'data/mrs_person_attributes_data.xml',
	     'views/event_records_view.xml',
             'views/res_company.xml',
             'wizard/stock_location_product_dhis2.xml',
             'views/order_type_view.xml',
             'views/syncable_units_view.xml',
             'views/order_type_shop_map_view.xml',
             'views/res_users_view.xml',
             ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
