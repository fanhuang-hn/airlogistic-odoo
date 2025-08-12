# -*- coding: utf-8 -*-
{
    'name': 'Simple Sample Addon',
    'version': '18.0.1.0.0',
    'category': 'Custom Development',
    'summary': 'Simple addon for demonstration',
    'description': """
        A very simple addon for testing Odoo development setup.
    """,
    'author': 'Your Name',
    'website': 'https://your-website.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/simple_model_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
