# -*- coding: utf-8 -*-

{
    'name': 'Payment Provider: DUC',
    'category': 'Accounting/Payment',
    'author': 'Volttus Inc.',
    'summary': 'Payment Provider: DUC',
    'version': '1.0',
    'description': """Payment Provider: DUC""",
    'depends': ['payment','website','website_sale'],
    'data': [

        'views/payment_ducapi3_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            '/payment_duc/static/src/js/post_processing.js',
         ]
    },

    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
