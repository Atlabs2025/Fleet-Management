from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    job_card_id = fields.Many2one('job.card.management', string="Job Card")
    excess_amount = fields.Float(string="Excess Amount")

    service_contract_id = fields.Many2one('fleet.vehicle.log.contract', string="Service Contract")

    # insurance_company_id = fields.Many2one('res.partner', string='Insurance Company')

    # @api.onchange('job_card_id')
    # def _onchange_job_card_id(self):
    #     if self.job_card_id and self.move_type == 'in_invoice':
    #         # Existing invoice lines remove cheyyu
    #         self.invoice_line_ids = [(5, 0, 0)]  # Remove all existing lines
    #
    #         # Job Card-il sublet department-ile lines matram fetch cheyyu
    #         sublet_lines = self.job_card_id.job_detail_line_ids.filtered(lambda l: l.department == 'sublets')
    #
    #         # Invoice lines prepare cheyyu
    #         lines = []
    #         for line in sublet_lines:
    #             if line.product_template_id:
    #                 product = line.product_template_id.product_variant_id
    #                 lines.append((0, 0, {
    #                     'product_id': f"{line.department or ''} - {line.description}",
    #                     'quantity': line.quantity,
    #                     'price_unit': line.price_unit,
    #                     # 'discount': line.discount,
    #                     'tax_ids': [(6, 0, line.tax_ids.ids)],
    #                     # 'account_id': product.property_account_expense_id.id or product.categ_id.property_account_expense_categ_id.id,
    #                 }))
    #
    #         # Set the invoice lines
    #         self.invoice_line_ids = lines
