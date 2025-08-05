# -*- coding: utf-8 -*-
{
    'name': 'Sample Addon',
    'version': '18.0.1.0.0',
    'category': 'Custom Development',
    'summary': 'Sample addon for demonstration purposes',
    'description': """
        This is a sample addon created to demonstrate the structure
        and best practices for Odoo addon development.
        
        Features:
        - Sample model with basic fields
        - List and form views
        - Menu structure
        - Security configuration
        - Demo data
    """,
    'author': 'Your Name',
    'website': 'https://your-website.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sample_data.xml',
        'views/menu_views.xml',
        'views/sample_model_views.xml',
        'wizard/sample_wizard_views.xml',
    ],
    'demo': [
        'demo/sample_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sample_addon/static/src/css/sample.css',
            'sample_addon/static/src/js/sample.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,  # This is a standalone application
}
