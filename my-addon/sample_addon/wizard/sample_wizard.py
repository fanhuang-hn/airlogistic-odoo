# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SampleWizard(models.TransientModel):
    """Wizard for bulk operations on sample records"""
    _name = 'sample.wizard'
    _description = 'Sample Wizard'

    operation = fields.Selection([
        ('confirm', 'Confirm Selected Records'),
        ('start_progress', 'Start Progress on Selected Records'),
        ('mark_done', 'Mark Selected Records as Done'),
        ('cancel', 'Cancel Selected Records'),
        ('update_progress', 'Update Progress'),
        ('assign_user', 'Assign Responsible User'),
        ('add_tags', 'Add Tags'),
    ], string='Operation', required=True, default='confirm')

    # Fields for specific operations
    progress_value = fields.Float('Progress Value (%)', digits=(5, 2),
                                 help='New progress value (0-100)')
    user_id = fields.Many2one('res.users', 'Assign to User')
    tag_ids = fields.Many2many('sample.model.tag', string='Tags to Add')
    
    # Information fields
    record_count = fields.Integer('Selected Records', readonly=True)
    record_info = fields.Text('Record Information', readonly=True)

    @api.model
    def default_get(self, fields):
        """Get default values based on selected records"""
        res = super().default_get(fields)
        
        # Get active records
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_('No records selected.'))
        
        records = self.env['sample.model'].browse(active_ids)
        
        # Set record information
        res['record_count'] = len(records)
        record_names = records.mapped('name')[:5]  # Show first 5 names
        if len(records) > 5:
            record_names.append(f'... and {len(records) - 5} more')
        res['record_info'] = '\n'.join(record_names)
        
        return res

    @api.onchange('operation')
    def _onchange_operation(self):
        """Clear fields when operation changes"""
        self.progress_value = 0.0
        self.user_id = False
        self.tag_ids = [(5,)]

    def action_execute(self):
        """Execute the selected operation"""
        self.ensure_one()
        
        # Get selected records
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['sample.model'].browse(active_ids)
        
        if not records:
            raise UserError(_('No records to process.'))
        
        # Execute operation based on selection
        if self.operation == 'confirm':
            self._confirm_records(records)
        elif self.operation == 'start_progress':
            self._start_progress_records(records)
        elif self.operation == 'mark_done':
            self._mark_done_records(records)
        elif self.operation == 'cancel':
            self._cancel_records(records)
        elif self.operation == 'update_progress':
            self._update_progress_records(records)
        elif self.operation == 'assign_user':
            self._assign_user_records(records)
        elif self.operation == 'add_tags':
            self._add_tags_records(records)
        
        return {'type': 'ir.actions.act_window_close'}

    def _confirm_records(self, records):
        """Confirm selected records"""
        draft_records = records.filtered(lambda r: r.state == 'draft')
        if not draft_records:
            raise UserError(_('No draft records to confirm.'))
        
        draft_records.write({'state': 'confirmed'})
        
        # Post message to each record
        for record in draft_records:
            record.message_post(
                body=_('Record confirmed via bulk operation by %s') % self.env.user.name
            )

    def _start_progress_records(self, records):
        """Start progress on selected records"""
        confirmed_records = records.filtered(lambda r: r.state == 'confirmed')
        if not confirmed_records:
            raise UserError(_('No confirmed records to start progress.'))
        
        confirmed_records.write({'state': 'in_progress'})
        
        # Post message to each record
        for record in confirmed_records:
            record.message_post(
                body=_('Progress started via bulk operation by %s') % self.env.user.name
            )

    def _mark_done_records(self, records):
        """Mark selected records as done"""
        valid_records = records.filtered(lambda r: r.state in ['confirmed', 'in_progress'])
        if not valid_records:
            raise UserError(_('No valid records to mark as done.'))
        
        valid_records.write({
            'state': 'done',
            'progress': 100.0
        })
        
        # Post message to each record
        for record in valid_records:
            record.message_post(
                body=_('Record completed via bulk operation by %s') % self.env.user.name
            )

    def _cancel_records(self, records):
        """Cancel selected records"""
        cancellable_records = records.filtered(lambda r: r.state != 'done')
        if not cancellable_records:
            raise UserError(_('No records can be cancelled.'))
        
        cancellable_records.write({'state': 'cancelled'})
        
        # Post message to each record
        for record in cancellable_records:
            record.message_post(
                body=_('Record cancelled via bulk operation by %s') % self.env.user.name
            )

    def _update_progress_records(self, records):
        """Update progress on selected records"""
        if not (0 <= self.progress_value <= 100):
            raise UserError(_('Progress value must be between 0 and 100.'))
        
        active_records = records.filtered(lambda r: r.state in ['confirmed', 'in_progress'])
        if not active_records:
            raise UserError(_('No active records to update progress.'))
        
        active_records.write({'progress': self.progress_value})
        
        # Post message to each record
        for record in active_records:
            record.message_post(
                body=_('Progress updated to %s%% via bulk operation by %s') % (
                    self.progress_value, self.env.user.name
                )
            )

    def _assign_user_records(self, records):
        """Assign user to selected records"""
        if not self.user_id:
            raise UserError(_('Please select a user to assign.'))
        
        records.write({'user_id': self.user_id.id})
        
        # Post message to each record
        for record in records:
            record.message_post(
                body=_('Assigned to %s via bulk operation by %s') % (
                    self.user_id.name, self.env.user.name
                )
            )

    def _add_tags_records(self, records):
        """Add tags to selected records"""
        if not self.tag_ids:
            raise UserError(_('Please select tags to add.'))
        
        for record in records:
            # Add tags without removing existing ones
            record.tag_ids = [(4, tag.id) for tag in self.tag_ids]
            record.message_post(
                body=_('Tags added: %s via bulk operation by %s') % (
                    ', '.join(self.tag_ids.mapped('name')), self.env.user.name
                )
            )
