# -*- coding: utf-8 -*-
{
    'name': 'Bahmni Product',
    'version': '1.0',
    'summary': 'Custom product module to meet bahmni requirement',
    'sequence': 1,
    'description': """
Bahmni Product
====================
""",
    'category': 'Product',
    'website': '',
    'images': [],
    'depends': ['product', 'product_expiry'],
    'data': ['data/product_category.xml',
             'views/res_partner_view.xml',
             'views/product_supplierinfo_view.xml',
             'views/product_view.xml'],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
