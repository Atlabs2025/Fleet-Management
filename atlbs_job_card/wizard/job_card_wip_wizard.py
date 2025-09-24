from odoo import models, fields

class JobCardWIPWizard(models.TransientModel):
    _name = "job.card.wip.wizard"
    _description = "WIP Job Card Report Wizard"

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    # due_days_label = fields.Char(string="Due Days Label")

    # def action_print_report(self):
    #     self.ensure_one()
    #     return self.env.ref('atlbs_job_card.action_report_job_card_not_completed').report_action(self, data={
    #         'date_from': self.date_from,
    #         'date_to': self.date_to
    #     })

    def action_print_report(self):
        self.ensure_one()
        job_cards = self.env['job.card.management'].search([
            ('state', '!=', 'completed'),
            ('created_datetime', '>=', self.date_from),
            ('created_datetime', '<=', self.date_to),
        ])
        return self.env.ref('atlbs_job_card.action_report_job_card_not_completed').report_action(
            job_cards
        )



