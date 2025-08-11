# -*- coding: utf-8 -*-

from odoo import fields, models


class QualityChecklist(models.Model):
    _name = "quality.checklist"
    _description = 'Quality Checklist'

    # name = fields.Char(
    #     string = "Name",
    #     required=True,
    #     copy=False
    # )
    # description = fields.Text(
    #     string = "Description"
    # )
    #
    # checklist_name_id = fields.Many2one(
    #     'quality.checklist.name',
    #     string="Checklist Name",
    #     required=True
    # )

    job_card_id = fields.Many2one('job.card.management', string='Job Card', required=True, ondelete='cascade')
    name = fields.Char(string='Checklist Item', required=True)
    checklist_name_id = fields.Many2one('quality.checklist.name', string='Checklist Category')
    serial_no = fields.Integer(string='Serial Number', default=10)
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], string='Display Type', default=False, help="Technical field for sections and notes")
    check_mark = fields.Boolean(string='Checked')
    description = fields.Text(string='Description')
