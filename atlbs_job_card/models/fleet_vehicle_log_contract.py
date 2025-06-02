from odoo import fields, models


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    total_services = fields.Integer(string="Total Services")
    contract_cost = fields.Float(string="Contract Cost")

    job_card_count = fields.Integer(
        string="Job Card Count", compute="_compute_job_card_count"
    )

    def _compute_job_card_count(self):
        for rec in self:
            rec.job_card_count = self.env['job.card.management'].search_count([
                ('service_contract_id', '=', rec.id)
            ])


    def action_view_job_cards(self):
        return {
            'name': 'Job Cards',
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.management',
            'view_mode': 'list,form',
            'domain': [('service_contract_id', '=', self.id)],
            'context': {'default_service_contract_id': self.id},
            'target': 'current',
        }