from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    timesheet_ids = fields.One2many(
        'account.analytic.line',
        'employee_id',
        string="Timesheets"
    )
