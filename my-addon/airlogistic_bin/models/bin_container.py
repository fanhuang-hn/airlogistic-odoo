# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AirlogisticBin(models.Model):
    """Bin container model for air logistics"""
    _name = 'airlogistic.bin'
    _description = 'Airlogistic Bin Container'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'bin_code, id'

    # Basic bin information
    bin_code = fields.Char('Bin Code', required=True, tracking=True, 
                          help='Unique identifier for the bin container')
    name = fields.Char('Name', compute='_compute_name', store=True, 
                      help='Display name combining code and type')
    
    # Bin type and specifications
    bin_type = fields.Selection([
        ('uld', 'ULD (Unit Load Device)'),
        ('pallet', 'Pallet'),
        ('container', 'Container'),
        ('bulk', 'Bulk Cargo'),
        ('special', 'Special Cargo'),
    ], string='Bin Type', required=True, tracking=True, default='container')
    
    bin_subtype = fields.Char('Bin Subtype', help='Specific subtype (e.g., LD3, LD7, PMC)')
    
    # Physical specifications
    volume = fields.Float('Volume (m³)', required=True, digits=(10, 3),
                         help='Physical volume capacity in cubic meters')
    max_weight = fields.Float('Max Weight (kg)', required=True, digits=(10, 2),
                             help='Maximum weight capacity in kilograms')
    current_weight = fields.Float('Current Weight (kg)', digits=(10, 2), 
                                 tracking=True, help='Current loaded weight')
    
    # Dimensions (optional)
    length = fields.Float('Length (cm)', digits=(8, 2))
    width = fields.Float('Width (cm)', digits=(8, 2))
    height = fields.Float('Height (cm)', digits=(8, 2))
    
    # Flight assignment
    flight_id = fields.Many2one('airlogistic.flight', 'Assigned Flight', 
                               tracking=True, ondelete='set null',
                               help='Flight this bin is assigned to')
    flight_number = fields.Char('Flight Number', related='flight_id.flight_number', 
                               store=True, readonly=True)
    flight_state = fields.Selection(related='flight_id.state', store=True, readonly=True)
    
    # Status and computed fields
    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned to Flight'),
        ('loaded', 'Loaded'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('maintenance', 'Under Maintenance'),
    ], string='Bin Status', default='available', tracking=True, compute='_compute_state', store=True)
    
    # Weight management
    available_weight = fields.Float('Available Weight (kg)', compute='_compute_weight_info', 
                                   digits=(10, 2), help='Remaining weight capacity')
    weight_utilization = fields.Float('Weight Utilization (%)', compute='_compute_weight_info', 
                                     store=True, digits=(5, 2))
    is_overloaded = fields.Boolean('Is Overloaded', compute='_compute_weight_info', store=True,
                                  help='True if current weight exceeds maximum weight')
    
    # Location tracking
    current_location = fields.Char('Current Location', 
                                  help='Current physical location of the bin')
    
    # Additional information
    description = fields.Text('Description', help='Additional notes about the bin')
    barcode = fields.Char('Barcode', help='Barcode for bin identification')
    qr_code = fields.Char('QR Code', help='QR code for bin identification')
    
    # Maintenance and certification
    last_maintenance_date = fields.Date('Last Maintenance')
    next_maintenance_date = fields.Date('Next Maintenance')
    certification_expiry = fields.Date('Certification Expiry')
    
    # System fields
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', 
                                default=lambda self: self.env.company, required=True)
    
    # SQL constraints
    _sql_constraints = [
        ('bin_code_unique', 'unique(bin_code, company_id)', 
         'Bin code must be unique per company!'),
        ('positive_volume', 'CHECK(volume > 0)', 
         'Volume must be positive!'),
        ('positive_max_weight', 'CHECK(max_weight > 0)', 
         'Maximum weight must be positive!'),
        ('positive_current_weight', 'CHECK(current_weight >= 0)', 
         'Current weight cannot be negative!'),
    ]
    
    @api.depends('bin_code', 'bin_type')
    def _compute_name(self):
        """Compute display name"""
        for bin_rec in self:
            type_label = dict(bin_rec._fields['bin_type'].selection).get(bin_rec.bin_type, '')
            bin_rec.name = f"[{bin_rec.bin_code}] {type_label}"
    
    @api.depends('flight_id', 'flight_id.state', 'current_weight')
    def _compute_state(self):
        """Compute bin state based on flight assignment and weight"""
        for bin_rec in self:
            if not bin_rec.flight_id:
                bin_rec.state = 'available'
            elif bin_rec.flight_id.state == 'scheduled':
                if bin_rec.current_weight > 0:
                    bin_rec.state = 'loaded'
                else:
                    bin_rec.state = 'assigned'
            elif bin_rec.flight_id.state in ['boarding', 'departed']:
                bin_rec.state = 'in_transit'
            elif bin_rec.flight_id.state == 'arrived':
                bin_rec.state = 'delivered'
            else:
                bin_rec.state = 'available'
    
    @api.depends('current_weight', 'max_weight')
    def _compute_weight_info(self):
        """Compute weight-related information"""
        for bin_rec in self:
            bin_rec.available_weight = bin_rec.max_weight - bin_rec.current_weight
            bin_rec.weight_utilization = (
                (bin_rec.current_weight / bin_rec.max_weight * 100) 
                if bin_rec.max_weight else 0.0
            )
            bin_rec.is_overloaded = bin_rec.current_weight > bin_rec.max_weight
    
    @api.constrains('current_weight', 'max_weight')
    def _check_weight_limit(self):
        """Validate weight constraints"""
        for bin_rec in self:
            if bin_rec.current_weight > bin_rec.max_weight:
                raise ValidationError(_(
                    'Current weight (%.2f kg) cannot exceed maximum weight (%.2f kg) for bin %s'
                ) % (bin_rec.current_weight, bin_rec.max_weight, bin_rec.bin_code))
    
    @api.constrains('flight_id')
    def _check_flight_modification(self):
        """Prevent flight modification after takeoff"""
        for bin_rec in self:
            if bin_rec.flight_id and bin_rec.flight_id.is_departed:
                # Check if this is a modification of existing record
                if bin_rec.id:
                    old_bin = self.browse(bin_rec.id)
                    if old_bin.flight_id != bin_rec.flight_id:
                        raise ValidationError(_(
                            'Cannot modify flight assignment for bin %s. Flight %s has already departed.'
                        ) % (bin_rec.bin_code, bin_rec.flight_id.flight_number))
    
    @api.constrains('current_weight')
    def _check_weight_modification_after_departure(self):
        """Prevent weight modification after flight departure"""
        for bin_rec in self:
            if bin_rec.flight_id and bin_rec.flight_id.is_departed:
                # Check if weight is being modified
                if bin_rec.id:
                    old_bin = self.browse(bin_rec.id)
                    if old_bin.current_weight != bin_rec.current_weight:
                        raise ValidationError(_(
                            'Cannot modify weight for bin %s. Flight %s has already departed.'
                        ) % (bin_rec.bin_code, bin_rec.flight_id.flight_number))
    
    @api.onchange('flight_id')
    def _onchange_flight_id(self):
        """Warning when assigning to departed flight"""
        if self.flight_id and self.flight_id.is_departed:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Flight %s has already departed. You cannot assign bins to departed flights.') % 
                              self.flight_id.flight_number
                }
            }
    
    @api.onchange('current_weight', 'max_weight')
    def _onchange_weight(self):
        """Warning when weight exceeds limit"""
        if self.current_weight > self.max_weight:
            return {
                'warning': {
                    'title': _('Weight Overload Warning'),
                    'message': _('Current weight (%.2f kg) exceeds maximum capacity (%.2f kg). '
                               'This bin is overloaded!') % (self.current_weight, self.max_weight)
                }
            }
    
    def action_assign_to_flight(self):
        """Open wizard to assign bin to flight"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assign to Flight'),
            'res_model': 'airlogistic.bin.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_bin_id': self.id},
        }
    
    def action_unassign_from_flight(self):
        """Unassign bin from flight"""
        self.ensure_one()
        if self.flight_id and self.flight_id.is_departed:
            raise UserError(_('Cannot unassign bin from departed flight %s') % 
                           self.flight_id.flight_number)
        
        old_flight = self.flight_id.flight_number if self.flight_id else ''
        self.flight_id = False
        self.current_weight = 0.0
        
        if old_flight:
            self.message_post(body=_('Bin unassigned from flight %s') % old_flight)
    
    def action_reset_weight(self):
        """Reset current weight to zero"""
        self.ensure_one()
        if self.flight_id and self.flight_id.is_departed:
            raise UserError(_('Cannot modify weight. Flight %s has already departed.') % 
                           self.flight_id.flight_number)
        
        old_weight = self.current_weight
        self.current_weight = 0.0
        self.message_post(body=_('Weight reset from %.2f kg to 0.00 kg') % old_weight)
    
    def action_set_maintenance(self):
        """Set bin to maintenance mode"""
        self.ensure_one()
        if self.flight_id:
            raise UserError(_('Cannot set bin to maintenance while assigned to flight %s') % 
                           self.flight_id.flight_number)
        
        self.state = 'maintenance'
        self.message_post(body=_('Bin set to maintenance mode'))
    
    @api.model
    def get_available_bins(self, volume_needed=0, weight_needed=0):
        """Get available bins that meet capacity requirements"""
        domain = [
            ('state', '=', 'available'),
            ('active', '=', True),
            ('volume', '>=', volume_needed),
            ('max_weight', '>=', weight_needed),
        ]
        return self.search(domain)
    
    @api.model
    def get_overloaded_bins(self):
        """Get all overloaded bins"""
        return self.search([('is_overloaded', '=', True)])
    
    def name_get(self):
        """Custom name format"""
        result = []
        for bin_rec in self:
            name = f"[{bin_rec.bin_code}] {dict(bin_rec._fields['bin_type'].selection)[bin_rec.bin_type]}"
            if bin_rec.flight_id:
                name += f" → {bin_rec.flight_id.flight_number}"
            result.append((bin_rec.id, name))
        return result