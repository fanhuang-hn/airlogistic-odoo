# -*- coding: utf-8 -*-
{
    'name': 'Airlogistic Bin Management',
    'version': '18.0.1.0.0',
    'category': 'Logistics',
    'summary': 'Bin container management for air logistics',
    'description': """
        Airlogistic Bin Management System
        
        This module provides comprehensive bin management functionality for air logistics:
        
        Features:
        - Create and manage cargo bins (ULD, Pallet, Container, etc.)
        - Assign bins to flights
        - Weight and volume tracking
        - Bin capacity validation
        - Flight takeoff restrictions
        - Overload warnings
        
        User Story 2.1: Tạo bin chứa hàng
        - Bin Code management
        - Type classification (ULD, Pallet, Container,...)
        - Volume and weight tracking
        - Flight assignment
        - Capacity constraints and validation
    """,
    'author': 'Airlogistic Team',
    'website': 'https://airlogistic.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/bin_type_data.xml',
        'views/menu_views.xml',
        'views/flight_views.xml',
        'views/bin_views.xml',
    ],
    'demo': [
        'demo/bin_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'airlogistic_bin/static/src/css/*.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}