# -*- coding: utf-8 -*-
{
    'name': 'Air Logistics - Flight Management',
    'version': '18.0.1.0.0',
    'category': 'Operations/Air Logistics',
    'summary': 'Manage flights, schedules, and air logistics operations',
    'description': """
        Air Logistics - Flight Management System
        
        This addon provides comprehensive flight management functionality for air logistics operations:
        
        Flight Management Features:
        - Create and manage flight schedules
        - Track flight status (Scheduled/Departed/Landed/Cancelled)
        - Airport management with IATA codes
        - Carrier information management
        - Flight duration calculations
        - Status workflow management
        
        Constraints and Validations:
        - Flight numbers must be unique per day
        - Arrival time must be after departure time
        - IATA airport code validation
        - Status workflow controls
        
        Views and Features:
        - Comprehensive form view with statusbar
        - List view with filtering and grouping
        - Kanban view grouped by status
        - Calendar view for schedule overview
        - Advanced search and filtering options
        
        Sample addon structure for demonstration purposes is also included.
    """,
    'author': 'Your Name',
    'website': 'https://your-website.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sample_data.xml',
        'views/menu_views.xml',
        'views/flight_views.xml',
        'views/sample_model_views.xml',
        'wizard/sample_wizard_views.xml',
    ],
    'demo': [
        'demo/sample_demo.xml',
        'demo/flight_demo.xml',
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
