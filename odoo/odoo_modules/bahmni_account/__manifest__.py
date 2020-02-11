# -*- coding: utf-8 -*-
{
    'name': 'Bahmni Account',
    'version': '1.0',
    'summary': 'Custom account module to meet bahmni requirement',
    'sequence': 1,
    'description': """
Bahmni Account
====================
""",
    'category': 'Account',
    'website': '',
    'images': [],
    'depends': ['account', 'account_voucher', 'web_readonly_bypass'],
    'data': [
             'views/bahmni_account.xml',
             'views/account_invoice_view.xml',
             'views/account_config_settings.xml',
             'report/account_count_report.xml',
             'report/account_report.xml',
             'security/ir.model.access.csv',
             'views/account_payment.xml',
             'report/report_invoice_inherit.xml'
             ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
