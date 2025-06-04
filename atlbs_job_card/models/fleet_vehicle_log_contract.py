from odoo import fields, models, api
from odoo.exceptions import UserError


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    total_services = fields.Integer(string="Total Services")
    contract_cost = fields.Float(string="Contract Cost")

    job_card_count = fields.Integer(
        string="Job Card Count", compute="_compute_job_card_count"
    )
    contract_type = fields.Selection([
        ('reduce_by_service', 'Reduce Amount by Service'),
        ('fixed_services', 'Fixed Number of Services')
    ], string="Contract Type", required=True)

    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.company.currency_id)

    service_name_ids = fields.Many2many(
        'fleet.vehicle.service',
        string='Services')

    used_service_ids = fields.Many2many(
        'fleet.vehicle.service',
        'fleet_vehicle_log_contract_used_services_rel',  # <-- Custom relation table
        'contract_id',
        'service_id',
        string='Used Services',
        readonly=True,
        help="Services that have already been invoiced"
    )

    @api.onchange('service_name_ids')
    def _onchange_service_name_ids(self):
        if not self.used_service_ids or not self.service_name_ids:
            return

        # Check if any selected service is already used
        used = self.used_service_ids.ids
        selected = self.service_name_ids.ids
        already_used = set(used) & set(selected)

        if already_used:
            used_names = ', '.join(self.env['fleet.vehicle.service'].browse(already_used).mapped('name'))
            raise UserError(
                f"The following services have already been invoiced and cannot be selected again: {used_names}")



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



    def action_create_payment(self):
        self.ensure_one()

        if not self.service_name_ids:
            raise UserError("Please select at least one service.")

        if not self.contract_cost:
            raise UserError("Contract cost must be set.")

        # Build a combined service description
        service_descriptions = "\n".join(service.name for service in self.service_name_ids)

        invoice_line_vals = [{
            'name': f"Services:\n{service_descriptions}",
            'quantity': 1,
            'price_unit': self.contract_cost,
        }]

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.company_id.partner_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [(0, 0, line) for line in invoice_line_vals],
        })

        # Mark selected services as used
        self.used_service_ids = [(4, s.id) for s in self.service_name_ids]

        # Clear selected services after invoicing
        self.service_name_ids = [(5, 0, 0)]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }



    def action_close_contract(self):
        for record in self:
            record.state = 'closed'


class FleetVehicleService(models.Model):
    _name = 'fleet.vehicle.service'
    _description = 'Vehicle Service'

    name = fields.Char(string='Service Name', required=True)
    description = fields.Text(string='Description')
    cost = fields.Float(string='Service Cost')
