# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AirlogisticFlight(models.Model):
    """Flight model for air logistics"""
    _name = 'airlogistic.flight'
    _description = 'Airlogistic Flight'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'departure_date desc, flight_number'

    # Basic flight information
    flight_number = fields.Char('Flight Number', required=True, tracking=True, 
                               help='Flight identification number (e.g., VN123)')
    airline = fields.Char('Airline', required=True, tracking=True)
    aircraft_type = fields.Char('Aircraft Type', help='Aircraft model (e.g., Boeing 777, Airbus A320)')
    
    # Route information
    departure_airport = fields.Char('Departure Airport', required=True)
    arrival_airport = fields.Char('Arrival Airport', required=True)
    
    # Schedule
    departure_date = fields.Datetime('Departure Date', required=True, tracking=True)
    arrival_date = fields.Datetime('Arrival Date', required=True)
    
    # Flight status
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('arrived', 'Arrived'),
        ('cancelled', 'Cancelled'),
    ], string='Flight Status', default='scheduled', tracking=True, required=True)
    
    # Capacity information
    max_cargo_weight = fields.Float('Max Cargo Weight (kg)', digits=(10, 2),
                                   help='Maximum cargo weight capacity')
    max_cargo_volume = fields.Float('Max Cargo Volume (m³)', digits=(10, 2),
                                   help='Maximum cargo volume capacity')
    
    # Bin relationships
    bin_ids = fields.One2many('airlogistic.bin', 'flight_id', 'Assigned Bins')
    bin_count = fields.Integer('Bin Count', compute='_compute_bin_count')
    
    # Computed totals
    total_bin_weight = fields.Float('Total Bin Weight (kg)', compute='_compute_totals', 
                                   store=True, digits=(10, 2))
    total_bin_volume = fields.Float('Total Bin Volume (m³)', compute='_compute_totals', 
                                   store=True, digits=(10, 2))
    
    # Weight and volume utilization
    weight_utilization = fields.Float('Weight Utilization (%)', compute='_compute_utilization', 
                                     digits=(5, 2))
    volume_utilization = fields.Float('Volume Utilization (%)', compute='_compute_utilization', 
                                     digits=(5, 2))
    
    # Status flags
    is_departed = fields.Boolean('Has Departed', compute='_compute_status_flags')
    has_overloaded_bins = fields.Boolean('Has Overloaded Bins', compute='_compute_overload_status', store=True)
    
    # Additional fields
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', 
                                default=lambda self: self.env.company, required=True)
    
    @api.depends('bin_ids')
    def _compute_bin_count(self):
        """Compute number of assigned bins"""
        for flight in self:
            flight.bin_count = len(flight.bin_ids)
    
    @api.depends('bin_ids.current_weight', 'bin_ids.volume')
    def _compute_totals(self):
        """Compute total weight and volume from all bins"""
        for flight in self:
            flight.total_bin_weight = sum(flight.bin_ids.mapped('current_weight'))
            flight.total_bin_volume = sum(flight.bin_ids.mapped('volume'))
    
    @api.depends('total_bin_weight', 'total_bin_volume', 'max_cargo_weight', 'max_cargo_volume')
    def _compute_utilization(self):
        """Compute weight and volume utilization percentages"""
        for flight in self:
            flight.weight_utilization = (
                (flight.total_bin_weight / flight.max_cargo_weight * 100) 
                if flight.max_cargo_weight else 0.0
            )
            flight.volume_utilization = (
                (flight.total_bin_volume / flight.max_cargo_volume * 100) 
                if flight.max_cargo_volume else 0.0
            )
    
    @api.depends('state')
    def _compute_status_flags(self):
        """Compute status flags"""
        for flight in self:
            flight.is_departed = flight.state in ['departed', 'arrived']
    
    @api.depends('bin_ids.is_overloaded')
    def _compute_overload_status(self):
        """Check if any bin is overloaded"""
        for flight in self:
            flight.has_overloaded_bins = any(flight.bin_ids.mapped('is_overloaded'))
    
    @api.constrains('departure_date', 'arrival_date')
    def _check_flight_dates(self):
        """Validate flight dates"""
        for flight in self:
            if flight.arrival_date <= flight.departure_date:
                raise ValidationError(_('Arrival date must be after departure date.'))
    
    @api.constrains('max_cargo_weight', 'max_cargo_volume')
    def _check_capacity_values(self):
        """Validate capacity values"""
        for flight in self:
            if flight.max_cargo_weight < 0:
                raise ValidationError(_('Maximum cargo weight cannot be negative.'))
            if flight.max_cargo_volume < 0:
                raise ValidationError(_('Maximum cargo volume cannot be negative.'))
    
    def action_confirm_departure(self):
        """Mark flight as departed"""
        self.ensure_one()
        if self.state not in ['scheduled', 'boarding']:
            raise UserError(_('Only scheduled or boarding flights can depart.'))
        
        if self.has_overloaded_bins:
            raise UserError(_('Cannot depart flight with overloaded bins. Please check bin weights.'))
        
        self.state = 'departed'
        self.message_post(body=_('Flight %s has departed at %s') % (
            self.flight_number, fields.Datetime.now()))
    
    def action_confirm_arrival(self):
        """Mark flight as arrived"""
        self.ensure_one()
        if self.state != 'departed':
            raise UserError(_('Only departed flights can arrive.'))
        
        self.state = 'arrived'
        self.message_post(body=_('Flight %s has arrived at %s') % (
            self.flight_number, fields.Datetime.now()))
    
    def action_cancel_flight(self):
        """Cancel the flight"""
        self.ensure_one()
        if self.state in ['departed', 'arrived']:
            raise UserError(_('Cannot cancel flights that have already departed or arrived.'))
        
        self.state = 'cancelled'
        self.message_post(body=_('Flight %s has been cancelled') % self.flight_number)
    
    def action_view_bins(self):
        """Open bin management view for this flight"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Flight Bins: %s') % self.flight_number,
            'res_model': 'airlogistic.bin',
            'view_mode': 'tree,form',
            'domain': [('flight_id', '=', self.id)],
            'context': {'default_flight_id': self.id},
            'target': 'current',
        }
    
    @api.model
    def name_get(self):
        """Custom name format"""
        result = []
        for flight in self:
            name = f"{flight.flight_number} ({flight.departure_airport} → {flight.arrival_airport})"
            result.append((flight.id, name))
        return result