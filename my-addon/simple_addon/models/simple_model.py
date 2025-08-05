# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SimpleModel(models.Model):
    _name = 'simple.model'
    _description = 'Simple Model'
    _order = 'name'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
