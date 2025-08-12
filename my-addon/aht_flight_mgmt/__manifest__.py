# -*- coding: utf-8 -*-
{
    'name': 'AHT Flight Management',
    'version': '18.0.1.0.0',
    'category': 'Operations/Inventory',
    'summary': 'Flight Management System for Air Logistics Operations',
    'description': """
        Flight Management System for Air Logistics Operations
        ====================================================
        
        This module provides comprehensive flight management functionality including:
        * Flight scheduling and tracking
        * Airport management with IATA code validation
        * Flight status workflow (Scheduled → Departed → Landed)
        * Carrier and route management
        * Duration calculation and reporting
        
        Perfect for airlines, logistics companies, and airport operations.
    """,
    'author': 'AHT Logistics',
    'website': 'https://aht-logistics.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/flight_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/flight_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}