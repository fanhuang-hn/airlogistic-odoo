# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class SampleController(http.Controller):
    """Controller for sample addon web endpoints"""

    @http.route('/sample/records', type='http', auth='user', website=True)
    def sample_records_portal(self, **kwargs):
        """Portal page to display sample records"""
        records = request.env['sample.model'].search([
            ('user_id', '=', request.env.user.id)
        ])
        
        values = {
            'records': records,
            'page_name': 'sample_records',
        }
        return request.render('sample_addon.portal_sample_records', values)

    @http.route('/sample/record/<int:record_id>', type='http', auth='user', website=True)
    def sample_record_detail(self, record_id, **kwargs):
        """Detailed view of a sample record"""
        record = request.env['sample.model'].browse(record_id)
        
        # Check access rights
        if not record.exists() or record.user_id != request.env.user:
            return request.not_found()
        
        values = {
            'record': record,
            'page_name': 'sample_record_detail',
        }
        return request.render('sample_addon.portal_sample_record_detail', values)

    @http.route('/sample/api/records', type='json', auth='user', methods=['GET'])
    def api_get_records(self, **kwargs):
        """JSON API endpoint to get sample records"""
        domain = []
        
        # Add filters based on parameters
        if kwargs.get('state'):
            domain.append(('state', '=', kwargs['state']))
        if kwargs.get('user_id'):
            domain.append(('user_id', '=', int(kwargs['user_id'])))
        if kwargs.get('priority'):
            domain.append(('priority', '=', kwargs['priority']))
        
        # Limit and offset for pagination
        limit = int(kwargs.get('limit', 10))
        offset = int(kwargs.get('offset', 0))
        
        records = request.env['sample.model'].search(
            domain, limit=limit, offset=offset, order='id desc'
        )
        
        # Prepare response data
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'name': record.name,
                'state': record.state,
                'priority': record.priority,
                'progress': record.progress,
                'user_id': record.user_id.id,
                'user_name': record.user_id.name,
                'partner_id': record.partner_id.id if record.partner_id else None,
                'partner_name': record.partner_id.name if record.partner_id else None,
                'total_amount': record.total_amount,
                'currency': record.currency_id.name,
                'date_created': record.date_created.isoformat() if record.date_created else None,
                'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in record.tag_ids],
            })
        
        return {
            'status': 'success',
            'data': data,
            'total': request.env['sample.model'].search_count(domain),
            'limit': limit,
            'offset': offset,
        }

    @http.route('/sample/api/record/<int:record_id>/update', type='json', auth='user', methods=['POST'])
    def api_update_record(self, record_id, **kwargs):
        """JSON API endpoint to update a sample record"""
        try:
            record = request.env['sample.model'].browse(record_id)
            
            if not record.exists():
                return {'status': 'error', 'message': 'Record not found'}
            
            # Check if user can modify this record
            if record.user_id != request.env.user and not request.env.user.has_group('base.group_system'):
                return {'status': 'error', 'message': 'Access denied'}
            
            # Update allowed fields
            update_vals = {}
            allowed_fields = ['name', 'description', 'priority', 'progress']
            
            for field in allowed_fields:
                if field in kwargs:
                    if field == 'progress':
                        progress = float(kwargs[field])
                        if 0 <= progress <= 100:
                            update_vals[field] = progress
                        else:
                            return {'status': 'error', 'message': 'Progress must be between 0 and 100'}
                    else:
                        update_vals[field] = kwargs[field]
            
            if update_vals:
                record.write(update_vals)
                record.message_post(
                    body=f'Record updated via API by {request.env.user.name}'
                )
            
            return {
                'status': 'success',
                'message': 'Record updated successfully',
                'data': {
                    'id': record.id,
                    'name': record.name,
                    'state': record.state,
                    'progress': record.progress,
                }
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @http.route('/sample/api/stats', type='json', auth='user', methods=['GET'])
    def api_get_stats(self, **kwargs):
        """JSON API endpoint to get statistics"""
        domain = [('user_id', '=', request.env.user.id)]
        
        # Get counts by state
        states = ['draft', 'confirmed', 'in_progress', 'done', 'cancelled']
        state_counts = {}
        
        for state in states:
            count = request.env['sample.model'].search_count(
                domain + [('state', '=', state)]
            )
            state_counts[state] = count
        
        # Get priority counts
        priorities = ['low', 'normal', 'high', 'urgent']
        priority_counts = {}
        
        for priority in priorities:
            count = request.env['sample.model'].search_count(
                domain + [('priority', '=', priority)]
            )
            priority_counts[priority] = count
        
        # Calculate average progress
        records = request.env['sample.model'].search(domain)
        avg_progress = sum(records.mapped('progress')) / len(records) if records else 0
        
        return {
            'status': 'success',
            'data': {
                'total_records': len(records),
                'state_counts': state_counts,
                'priority_counts': priority_counts,
                'average_progress': round(avg_progress, 2),
                'total_amount': sum(records.mapped('total_amount')),
            }
        }
