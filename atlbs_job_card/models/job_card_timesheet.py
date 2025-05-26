from datetime import datetime
datetime.now()
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_time = fields.Float(string="Start Time")
    pause_time = fields.Float(string="Pause Time")
    end_time = fields.Float(string="End Time")
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('done', 'Completed'),
    ], string="Status", default='new', tracking=True)

    assigned_hours = fields.Float(string="Assigned Hours")
    working_hours = fields.Float(string="Working Hours", compute="_compute_working_hours", store=True)
    job_card_id = fields.Many2one('job.card.management', string="Job Card")
    employee_id = fields.Many2one('hr.employee', string="Technician")
    pause_start = fields.Float(string="Pause Start Time")
    pause_duration = fields.Float(string="Pause Duration", default=0.0)

    job_card_time_sheet_id = fields.Many2one('job.card.time.sheet', string="Time Sheet")

    def _get_current_time_float(self):
        now = datetime.now()
        return now.hour + now.minute / 60.0 + now.second / 3600.0

    def action_start(self):
        current_time = self._get_current_time_float()
        self.write({
            'start_time': current_time,
            'status': 'in_progress',
            'pause_duration': 0.0,
            'pause_start': 0.0,
        })

    def action_pause(self):
        now = self._get_current_time_float()
        self.write({
            'pause_start': now,
            'status': 'paused',
        })

    def action_resume(self):
        for rec in self:
            if rec.pause_start:
                now = rec._get_current_time_float()
                pause_time = now - rec.pause_start
                rec.write({
                    'pause_duration': rec.pause_duration + pause_time,
                    'pause_start': 0.0,
                    'status': 'in_progress',
                })

    def action_end(self):
        current_time = self._get_current_time_float()
        self.write({
            'end_time': current_time,
            'status': 'done',
        })

    @api.depends('start_time', 'end_time', 'pause_duration', 'status')
    def _compute_working_hours(self):
        for rec in self:
            if rec.status == 'done' and rec.start_time and rec.end_time:
                pause = rec.pause_duration or 0.0
                rec.working_hours = max((rec.end_time - rec.start_time) - pause, 0.0)
            else:
                rec.working_hours = 0.0


# added for creation time sheet from this to job card
    @api.model
    def create(self, vals):
        # First, create the analytic line
        analytic = super().create(vals)

        # Then create the job card time sheet, but avoid recursion by NOT calling back into analytic line
        if analytic.job_card_id:
            self.env['job.card.time.sheet'].create({
                'job_card_id': analytic.job_card_id.id,
                'employee_id': analytic.employee_id.id,
                'start_time': analytic.start_time,
                'pause_time': analytic.pause_time,
                'end_time': analytic.end_time,
                'status': analytic.status,
                'working_hours': analytic.working_hours,
                'assigned_hours': analytic.assigned_hours,
                'analytic_line_id': analytic.id,  # store link
                'name': analytic.name,
                'date': analytic.date,
            })

        return analytic
