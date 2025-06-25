from collections import defaultdict

from odoo import models, fields, api
from odoo.exceptions import UserError


class JobCardCostAnalysisWizard(models.TransientModel):
    _name = 'job.card.cost.analysis.wizard'
    _description = 'Job Card Cost Analysis Wizard'


    job_card_id = fields.Many2one('job.card.management', string='Job Card', required=True)
    # date_from = fields.Date(string="Date From")
    # date_to = fields.Date(string="Date To")

    # def action_print_report(self):
    #     data = {'job_card_id': self.job_card_id.id}
    #     return self.env.ref('atlbs_job_card.action_report_job_card_cost_analysis').report_action(self, data=data)

    def action_print_report(self):
        data = {
            'job_card_id': self.job_card_id.id,
            # 'date_from': self.date_from.isoformat(),
            # 'date_to': self.date_to.isoformat(),
        }
        return self.env.ref('atlbs_job_card.action_report_job_card_cost_analysis').report_action(self, data=data)


class ReportJobCardCostAnalysis(models.AbstractModel):
    _name = 'report.atlbs_job_card.report_job_card_cost_analysis'
    _description = 'Job Card Cost Analysis Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        job_card_id = data.get('job_card_id')
        # date_from = data.get('date_from')
        # date_to = data.get('date_to')

        job_card = self.env['job.card.management'].browse(job_card_id)

        DEPT_LABELS = {
            'labour': 'Labour Charges',
            'parts': 'Spare Parts',
            'material': 'Materials',
            'sublets': 'Sublet',
            'paint_material': 'Paint & Materials',
            'tyre': 'Tyre',
            'lubricant': 'Lubricant',
        }

        # Outgoing invoices (revenue)
        invoices = self.env['account.move'].search([
            ('job_card_id', '=', job_card_id),
            ('move_type', '=', 'out_invoice'),
            ('state', 'in', ['draft', 'posted']),

        ])

        # Incoming vendor bills (costs)
        vendor_bills = self.env['account.move'].search([
            ('job_card_id', '=', job_card_id),
            ('move_type', '=', 'in_invoice'),
            ('state', 'in', ['draft', 'posted']),

        ])

        revenue = defaultdict(float)
        for inv in invoices:
            for line in inv.invoice_line_ids:
                if line.department:
                    revenue[line.department] += line.price_subtotal

        cost = defaultdict(float)
        for bill in vendor_bills:
            for line in bill.invoice_line_ids:
                if line.department:
                    cost[line.department] += line.price_subtotal

        total_revenue = sum(revenue.values())
        total_cost = sum(cost.values())
        profit = total_revenue - total_cost

        return {
            'doc_ids': [job_card_id],
            'doc_model': 'job.card.management',
            'docs': job_card,
            'revenue_summary': {DEPT_LABELS.get(k, k): v for k, v in revenue.items()},
            'cost_summary': {DEPT_LABELS.get(k, k): v for k, v in cost.items()},
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'profit': profit,

        }



    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     job_card_id = data.get('job_card_id')
    #     job_card = self.env['job.card.management'].browse(job_card_id)
    #
    #     DEPT_LABELS = {
    #         'labour': 'Labour Charges',
    #         'parts': 'Spare Parts',
    #         'material': 'Materials',
    #         'sublets': 'Sublet',
    #         'paint_material': 'Paint & Materials',
    #         'tyre': 'Tyre',
    #         'lubricant': 'Lubricant',
    #     }
    #
    #     # Outgoing invoices
    #     invoices = self.env['account.move'].search([
    #         ('job_card_id', '=', job_card_id),
    #         ('move_type', '=', 'out_invoice'),
    #         ('state', 'in', ['draft', 'posted']),
    #     ])
    #
    #     # Vendor bills
    #     vendor_bills = self.env['account.move'].search([
    #         ('job_card_id', '=', job_card_id),
    #         ('move_type', '=', 'in_invoice'),
    #         ('state', 'in', ['draft', 'posted']),
    #     ])
    #
    #     # Revenue Summary
    #     revenue = defaultdict(float)
    #     for inv in invoices:
    #         for line in inv.invoice_line_ids:
    #             if line.department:
    #                 revenue[line.department] += line.price_subtotal
    #
    #     # Cost Summary
    #     cost = defaultdict(float)
    #     for bill in vendor_bills:
    #         for line in bill.invoice_line_ids:
    #             if line.department:
    #                 cost[line.department] += line.price_subtotal
    #
    #     total_revenue = sum(revenue.values())
    #     total_cost = sum(cost.values())
    #     profit = total_revenue - total_cost
    #
    #     return {
    #         'doc_ids': [job_card_id],
    #         'doc_model': 'job.card.management',
    #         'docs': job_card,
    #         'revenue_summary': {DEPT_LABELS.get(k, k): v for k, v in revenue.items()},
    #         'cost_summary': {DEPT_LABELS.get(k, k): v for k, v in cost.items()},
    #         'total_revenue': total_revenue,
    #         'total_cost': total_cost,
    #         'profit': profit,
    #     }
    #
