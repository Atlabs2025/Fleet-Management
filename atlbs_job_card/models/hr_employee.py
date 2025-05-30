from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    timesheet_ids = fields.One2many(
        'account.analytic.line',
        'employee_id',
        string="Timesheets"
    )



    employee_status = fields.Selection([
            ('available', 'Available'),
            ('not_available', 'Not Available'),
            ('annual_leave', 'Annual Leave'),
        ], string='Employee Status', default='available')