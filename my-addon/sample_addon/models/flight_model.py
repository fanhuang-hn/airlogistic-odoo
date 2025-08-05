# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date


class FlightFlight(models.Model):
    """Flight Management Model for Air Logistics"""
    _name = 'flight.flight'
    _description = 'Flight Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'departure_time desc, flight_number'

    # Basic flight information
    flight_number = fields.Char(
        'Flight Number', 
        required=True, 
        tracking=True,
        help='Unique flight number (e.g., VN123, QH456)'
    )
    
    # Airport codes (IATA format)
    departure_airport = fields.Char(
        'Departure Airport', 
        required=True, 
        size=3,
        tracking=True,
        help='IATA airport code (3 letters, e.g., HAN, SGN)'
    )
    arrival_airport = fields.Char(
        'Arrival Airport', 
        required=True, 
        size=3,
        tracking=True,
        help='IATA airport code (3 letters, e.g., HAN, SGN)'
    )
    
    # Flight times
    departure_time = fields.Datetime(
        'Departure Time', 
        required=True, 
        tracking=True,
        help='Scheduled departure time'
    )
    arrival_time = fields.Datetime(
        'Arrival Time', 
        required=True, 
        tracking=True,
        help='Scheduled arrival time'
    )
    
    # Flight status
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('departed', 'Departed'),
        ('landed', 'Landed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled', required=True, tracking=True)
    
    # Carrier information  
    carrier = fields.Char(
        'Carrier', 
        required=True, 
        tracking=True,
        help='Airline carrier name (e.g., Vietnam Airlines, Jetstar)'
    )
    
    # Additional fields for better functionality
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed fields
    flight_duration = fields.Float(
        'Duration (Hours)', 
        compute='_compute_flight_duration',
        help='Flight duration in hours'
    )
    departure_date = fields.Date(
        'Departure Date',
        compute='_compute_departure_date',
        store=True,
        help='Date of departure (for uniqueness constraint)'
    )
    
    @api.depends('departure_time', 'arrival_time')
    def _compute_flight_duration(self):
        """Compute flight duration in hours"""
        for flight in self:
            if flight.departure_time and flight.arrival_time:
                duration = flight.arrival_time - flight.departure_time
                flight.flight_duration = duration.total_seconds() / 3600
            else:
                flight.flight_duration = 0.0
    
    @api.depends('departure_time')
    def _compute_departure_date(self):
        """Compute departure date for constraint checking"""
        for flight in self:
            if flight.departure_time:
                flight.departure_date = flight.departure_time.date()
            else:
                flight.departure_date = False

    @api.constrains('departure_time', 'arrival_time')
    def _check_flight_times(self):
        """Validate that arrival time is after departure time"""
        for flight in self:
            if flight.departure_time and flight.arrival_time:
                if flight.arrival_time <= flight.departure_time:
                    raise ValidationError(_(
                        'Arrival time must be after departure time for flight %s'
                    ) % flight.flight_number)

    @api.constrains('departure_airport', 'arrival_airport')  
    def _check_airports(self):
        """Validate airport codes and ensure departure != arrival"""
        for flight in self:
            # Check IATA code format (3 uppercase letters)
            if flight.departure_airport:
                if len(flight.departure_airport) != 3 or not flight.departure_airport.isalpha():
                    raise ValidationError(_(
                        'Departure airport must be a 3-letter IATA code (e.g., HAN, SGN)'
                    ))
                flight.departure_airport = flight.departure_airport.upper()
                
            if flight.arrival_airport:
                if len(flight.arrival_airport) != 3 or not flight.arrival_airport.isalpha():
                    raise ValidationError(_(
                        'Arrival airport must be a 3-letter IATA code (e.g., HAN, SGN)'
                    ))
                flight.arrival_airport = flight.arrival_airport.upper()
                
            # Ensure departure and arrival airports are different
            if flight.departure_airport == flight.arrival_airport:
                raise ValidationError(_(
                    'Departure and arrival airports cannot be the same'
                ))

    @api.constrains('flight_number', 'departure_date')
    def _check_flight_number_unique_per_day(self):
        """Ensure flight number is unique within the same day"""
        for flight in self:
            if flight.flight_number and flight.departure_date:
                domain = [
                    ('flight_number', '=', flight.flight_number),
                    ('departure_date', '=', flight.departure_date),
                    ('id', '!=', flight.id),
                ]
                existing_flight = self.search(domain, limit=1)
                if existing_flight:
                    raise ValidationError(_(
                        'Flight number %s already exists for date %s'
                    ) % (flight.flight_number, flight.departure_date))

    def action_set_departed(self):
        """Set flight status to departed"""
        self.ensure_one()
        if self.status != 'scheduled':
            raise UserError(_('Only scheduled flights can be set to departed'))
        self.status = 'departed'
        self.message_post(body=_('Flight marked as departed by %s') % self.env.user.name)

    def action_set_landed(self):
        """Set flight status to landed"""
        self.ensure_one()
        if self.status != 'departed':
            raise UserError(_('Only departed flights can be set to landed'))
        self.status = 'landed'
        self.message_post(body=_('Flight marked as landed by %s') % self.env.user.name)

    def action_cancel_flight(self):
        """Cancel the flight"""
        self.ensure_one()
        if self.status in ['landed']:
            raise UserError(_('Landed flights cannot be cancelled'))
        self.status = 'cancelled'
        self.message_post(body=_('Flight cancelled by %s') % self.env.user.name)

    def action_reschedule_flight(self):
        """Reset flight to scheduled status"""
        self.ensure_one()
        if self.status == 'landed':
            raise UserError(_('Landed flights cannot be rescheduled'))
        self.status = 'scheduled'
        self.message_post(body=_('Flight rescheduled by %s') % self.env.user.name)

    def name_get(self):
        """Custom display name for flights"""
        result = []
        for flight in self:
            name = f"{flight.flight_number} ({flight.departure_airport}-{flight.arrival_airport})"
            result.append((flight.id, name))
        return result