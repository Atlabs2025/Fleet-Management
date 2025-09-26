from odoo import models, fields

class JobCardWIPWizard(models.TransientModel):
    _name = "job.card.wip.wizard"
    _description = "WIP Job Card Report Wizard"

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)

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

    # def action_view_report(self):
    #     self.ensure_one()
    #     job_cards = self.env['job.card.management'].search([
    #         ('state', '!=', 'completed'),
    #         ('created_datetime', '>=', self.date_from),
    #         ('created_datetime', '<=', self.date_to),
    #     ])
    #     action = {
    #         'type': 'ir.actions.act_window',
    #         'name': 'WIP Job Cards',
    #         'view_mode': 'tree,form',
    #         'res_model': 'job.card.management',
    #         'domain': [('id', 'in', job_cards.ids)],
    #         'target': 'current',
    #     }
    #     return action

    def action_view_report(self):
        """Open WIP Job Cards in list view"""
        self.ensure_one()
        job_cards = self.env['job.card.management'].search([
            ('state', '!=', 'completed'),
            ('created_datetime', '>=', self.date_from),
            ('created_datetime', '<=', self.date_to),
        ])
        return {
            'type': 'ir.actions.act_window',
            'name': 'WIP Job Cards',
            'res_model': 'job.card.management',
            'view_mode': 'list,form',
            'domain': [('id', 'in', job_cards.ids)],
            'target': 'current',
        }