# -*- coding: utf-8 -*-

from odoo import fields, models


class QualityChecklist(models.Model):
    _name = "quality.checklist"
    _description = 'Quality Checklist'


    job_card_id = fields.Many2one('job.card.management', string='Job Card', required=True, ondelete='cascade')
    name = fields.Char(string='Checklist Item', required=True)
    checklist_name_id = fields.Many2one('quality.checklist.name', string='Checklist Category')
    serial_no = fields.Integer(string='Serial Number', default=10)
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], string='Display Type', default=False, help="Technical field for sections and notes")

    is_ok = fields.Boolean(string='OK', default=False)
    repair_required = fields.Boolean(string='Required', default=False)
    replace_required = fields.Boolean(string='Replace Required', default=False)
    check_mark = fields.Boolean(string='Check Mark', default=False)
    remarks = fields.Char(string='Remarks')
    description = fields.Text(string='Description')
