from datetime import datetime
datetime.now()
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
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

    status_badge = fields.Html(
        string="Status",
        compute="_compute_status_badge",
        sanitize=False,
        store=True
    )

    assigned_hours = fields.Float(string="Assigned Hours")
    working_hours = fields.Float(string="Working Hours", compute="_compute_working_hours", store=True)
    job_card_id = fields.Many2one('job.card.management', string="Job Card")
    employee_id = fields.Many2one('hr.employee', string="Technician")
    pause_start = fields.Float(string="Pause Start Time")
    pause_duration = fields.Float(string="Pause Duration", default=0.0)

    job_card_time_sheet_id = fields.Many2one('job.card.time.sheet', string="Time Sheet")

    job_category_id = fields.Many2one(
        comodel_name='job.categories',
        string='Categories'
    )
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

    @api.depends('status')
    def _compute_status_badge(self):
        color_map = {
            'new': '#007bff',  # blue
            'in_progress': '#28a745',  # green
            'pause': '#fd7e14',  # orange
            'done': '#8b4513',  # brown
        }
        label_map = dict(self._fields['status'].selection)
        for rec in self:
            label = label_map.get(rec.status, '')
            color = color_map.get(rec.status, '#000000')
            rec.status_badge = (
                f'<span style="background-color:{color}; '
                f'color:white; padding:3px 8px; border-radius:4px; font-weight:600;">{label}</span>'
            )

    # added for creation time sheet from this to job card
#     @api.model
#     def create(self, vals):
#         # First, create the analytic line
#         analytic = super().create(vals)
#
#         # Then create the job card time sheet, but avoid recursion by NOT calling back into analytic line
#         if analytic.job_card_id:
#             self.env['job.card.time.sheet'].create({
#                 'job_card_id': analytic.job_card_id.id,
#                 'employee_id': analytic.employee_id.id,
#                 'start_time': analytic.start_time,
#                 'pause_time': analytic.pause_time,
#                 'end_time': analytic.end_time,
#                 'status': analytic.status,
#                 'working_hours': analytic.working_hours,
#                 'assigned_hours': analytic.assigned_hours,
#                 'analytic_line_id': analytic.id,  # store link
#                 'name': analytic.name,
#                 'date': analytic.date,
#             })
#
#         return analytic

    @api.model
    def create(self, vals):
        analytic = super().create(vals)

        # Create linked job card time sheet only if no recursion flag and job_card_id exists
        if not self.env.context.get('skip_timesheet_sync') and analytic.job_card_id:
            self.env['job.card.time.sheet'].with_context(skip_analytic_sync=True).create({
                'job_card_id': analytic.job_card_id.id,
                'employee_id': vals.get('employee_id'),
                'start_time': vals.get('start_time', 0.0),
                'pause_time': vals.get('pause_time', 0.0),
                'end_time': vals.get('end_time', 0.0),
                'status': vals.get('status', 'new'),
                'working_hours': vals.get('working_hours', 0.0),
                'assigned_hours': vals.get('assigned_hours', 0.0),
                'analytic_line_id': analytic.id,
                'job_category_id': analytic.job_category_id.id,
                'name': vals.get('name'),
                'date': vals.get('date'),
            })

        return analytic

    # def write(self, vals):
    #     res = super().write(vals)
    #     for rec in self:
    #         # Avoid recursion
    #         if self.env.context.get('skip_timesheet_sync'):
    #             continue
    #         if rec.job_card_time_sheet_id:
    #             rec.job_card_time_sheet_id.with_context(skip_analytic_sync=True).write({
    #                 'employee_id': vals.get('employee_id', rec.employee_id.id),
    #                 'start_time': vals.get('start_time', rec.start_time),
    #                 'pause_time': vals.get('pause_time', rec.pause_time),
    #                 'end_time': vals.get('end_time', rec.end_time),
    #                 'status': vals.get('status', rec.status),
    #                 'working_hours': vals.get('working_hours', rec.working_hours),
    #                 'assigned_hours': vals.get('assigned_hours', rec.assigned_hours),
    #                 'name': vals.get('name', rec.name),
    #                 'date': vals.get('date', rec.date),
    #             })
    #     return res



    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if self.env.context.get('skip_timesheet_sync'):
                continue
            if rec.job_card_time_sheet_id:
                _logger.info(
                    f"Syncing write from analytic line {rec.id} to job card time sheet {rec.job_card_time_sheet_id.id}")
                rec.job_card_time_sheet_id.with_context(skip_analytic_sync=True).write({
                    'employee_id': vals.get('employee_id', rec.employee_id.id),
                    'start_time': vals.get('start_time', rec.start_time),
                    'pause_time': vals.get('pause_time', rec.pause_time),
                    'end_time': vals.get('end_time', rec.end_time),
                    'status': vals.get('status', rec.status),
                    'working_hours': vals.get('working_hours', rec.working_hours),
                    'assigned_hours': vals.get('assigned_hours', rec.assigned_hours),
                    'job_category_id': rec.job_category_id.id,
                    'name': vals.get('name', rec.name),
                    'date': vals.get('date', rec.date),
                })
            else:
                _logger.warning(f"Analytic line {rec.id} has no linked job card time sheet")
        return res

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            in_progress = self.env['account.analytic.line'].search([
                ('employee_id', '=', self.employee_id.id),
                ('status', '=', 'in_progress'),
                ('id', '!=', self.id),  # exclude self
            ], limit=1)
            if in_progress:
                self.employee_id = False
                return {
                    'warning': {
                        'title': "Employee Already Assigned",
                        'message': "Employee Already Assigned 'In Progress' status."
                    }
                }
