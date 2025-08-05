# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SampleModel(models.Model):
    """Sample model demonstrating Odoo best practices"""
    _name = 'sample.model'
    _description = 'Sample Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, id desc'

    # Basic fields
    name = fields.Char('Name', required=True, tracking=True, 
                      help='Enter the name of the record')
    description = fields.Text('Description', help='Detailed description')
    active = fields.Boolean('Active', default=True, tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    
    # Selection field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)
    
    # Date fields
    date_created = fields.Date('Created Date', default=fields.Date.today)
    date_deadline = fields.Datetime('Deadline')
    
    # Numeric fields
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='normal')
    
    progress = fields.Float('Progress (%)', digits=(5, 2), 
                           help='Progress percentage (0-100)')
    amount = fields.Monetary('Amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', 'Currency', 
                                 default=lambda self: self.env.company.currency_id)
    
    # Relational fields
    partner_id = fields.Many2one('res.partner', 'Related Partner', 
                                help='Select the related partner')
    user_id = fields.Many2one('res.users', 'Responsible User', 
                             default=lambda self: self.env.user,
                             tracking=True)
    company_id = fields.Many2one('res.company', 'Company', 
                                default=lambda self: self.env.company,
                                required=True)
    
    # One2many field
    line_ids = fields.One2many('sample.model.line', 'sample_id', 'Lines')
    
    # Many2many field
    tag_ids = fields.Many2many('sample.model.tag', string='Tags')
    
    # Computed fields
    line_count = fields.Integer('Line Count', compute='_compute_line_count')
    total_amount = fields.Monetary('Total Amount', compute='_compute_total_amount', 
                                  store=True, currency_field='currency_id')
    
    # Display name
    display_name = fields.Char('Display Name', compute='_compute_display_name')

    @api.depends('line_ids')
    def _compute_line_count(self):
        """Compute the number of lines"""
        for record in self:
            record.line_count = len(record.line_ids)

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        """Compute total amount from lines"""
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    @api.depends('name', 'state')
    def _compute_display_name(self):
        """Compute display name"""
        for record in self:
            record.display_name = f"[{record.state.upper()}] {record.name}"

    @api.constrains('progress')
    def _check_progress(self):
        """Validate progress value"""
        for record in self:
            if record.progress < 0 or record.progress > 100:
                raise ValidationError(_('Progress must be between 0 and 100.'))

    @api.constrains('date_deadline')
    def _check_deadline(self):
        """Validate deadline is not in the past"""
        for record in self:
            if record.date_deadline and record.date_deadline < fields.Datetime.now():
                raise ValidationError(_('Deadline cannot be in the past.'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Update currency when partner changes"""
        if self.partner_id and self.partner_id.property_product_pricelist:
            self.currency_id = self.partner_id.property_product_pricelist.currency_id

    def action_confirm(self):
        """Confirm the record"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft records can be confirmed.'))
        self.state = 'confirmed'
        self.message_post(body=_('Record confirmed by %s') % self.env.user.name)

    def action_start_progress(self):
        """Start progress on the record"""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Only confirmed records can be started.'))
        self.state = 'in_progress'
        self.message_post(body=_('Progress started by %s') % self.env.user.name)

    def action_mark_done(self):
        """Mark record as done"""
        self.ensure_one()
        if self.state not in ['confirmed', 'in_progress']:
            raise UserError(_('Only confirmed or in-progress records can be completed.'))
        self.state = 'done'
        self.progress = 100.0
        self.message_post(body=_('Record completed by %s') % self.env.user.name)

    def action_cancel(self):
        """Cancel the record"""
        self.ensure_one()
        if self.state == 'done':
            raise UserError(_('Done records cannot be cancelled.'))
        self.state = 'cancelled'
        self.message_post(body=_('Record cancelled by %s') % self.env.user.name)

    def action_reset_to_draft(self):
        """Reset record to draft"""
        self.ensure_one()
        self.state = 'draft'
        self.progress = 0.0
        self.message_post(body=_('Record reset to draft by %s') % self.env.user.name)


class SampleModelLine(models.Model):
    """Sample model lines"""
    _name = 'sample.model.line'
    _description = 'Sample Model Line'
    _order = 'sequence, id'

    sample_id = fields.Many2one('sample.model', 'Sample', required=True, ondelete='cascade')
    name = fields.Char('Description', required=True)
    sequence = fields.Integer('Sequence', default=10)
    quantity = fields.Float('Quantity', default=1.0, digits='Product Unit of Measure')
    price = fields.Monetary('Price', currency_field='currency_id')
    amount = fields.Monetary('Amount', compute='_compute_amount', store=True, 
                            currency_field='currency_id')
    currency_id = fields.Many2one(related='sample_id.currency_id', store=True)

    @api.depends('quantity', 'price')
    def _compute_amount(self):
        """Compute line amount"""
        for line in self:
            line.amount = line.quantity * line.price


class SampleModelTag(models.Model):
    """Tags for sample model"""
    _name = 'sample.model.tag'
    _description = 'Sample Model Tag'
    _order = 'name'

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color', default=0)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name must be unique!'),
    ]
