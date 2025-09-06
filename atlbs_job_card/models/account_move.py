from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    job_card_id = fields.Many2one('job.card.management', string="Job Card")
    excess_amount = fields.Float(string="Excess Amount")

    service_advisor_id = fields.Many2one('res.users', string='Service Adviser', readonly=True,default=lambda self: self.env.user)

    service_contract_id = fields.Many2one('fleet.vehicle.log.contract', string="Service Contract")

    vehicle_make_id = fields.Many2one(
        'fleet.vehicle.model.brand',  # replace with your actual vehicle make model
        related='job_card_id.vehicle_make_id',
        store=True,
        string='Vehicle Make'
    )



# new fields  and functions added recently
#     discount_percent = fields.Float(string="Discount (%)", compute='_compute_discount_info', store=True)
#     amount_discount = fields.Monetary(string="Discount Amount", compute='_compute_discount_info', store=True)
#     amount_total_tax = fields.Monetary(string="Tax", compute='_compute_discount_info', store=True)
#     amount_grand_total = fields.Monetary(string="Grand Total", compute='_compute_discount_info', store=True)
#
#     @api.depends('invoice_line_ids.price_unit', 'invoice_line_ids.quantity',
#                  'invoice_line_ids.discount', 'invoice_line_ids.tax_ids', 'invoice_line_ids.price_subtotal')
#     def _compute_discount_info(self):
#         for move in self:
#             total = 0.0
#             discount_total = 0.0
#             tax_total = sum(move.amount_by_group and sum(t[1] for t in move.amount_by_group) or 0.0)
#             for line in move.invoice_line_ids:
#                 line_total = line.price_unit * line.quantity
#                 line_discount = line_total * (line.discount / 100.0)
#                 total += line_total
#                 discount_total += line_discount
#
#             move.amount_discount = discount_total
#             move.amount_total_tax = tax_total
#             move.amount_grand_total = move.amount_untaxed + tax_total - discount_total
#
#             if total:
#                 move.discount_percent = (discount_total / total) * 100
#             else:
#                 move.discount_percent = 0.0


    ##########################################


    @api.onchange('job_card_id')
    def _onchange_job_card_id(self):
        if self.job_card_id:
            self.partner_id = self.job_card_id.partner_id
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

    # def action_group_pay_now(self):
    #     for move in self:
    #         if move.state == 'draft':
    #             move.action_post()
    #         if move.payment_state != 'paid':
    #             payment_vals = {
    #                 'payment_type': 'inbound' if move.move_type == 'out_invoice' else 'outbound',
    #                 'partner_type': 'customer' if move.move_type == 'out_invoice' else 'supplier',
    #                 'partner_id': move.partner_id.id,
    #                 'amount': move.amount_total,
    #                 # 'payment_method_line_id': self.env.ref('account.account_payment_method_manual_in').id,
    #                 'journal_id': move.journal_id.id,
    #                 # 'payment_date': fields.Date.today(),
    #                 # 'communication': move.name,
    #                 'invoice_ids': [(6, 0, [move.id])],
    #             }
    #             payment = self.env['account.payment'].create(payment_vals)
    #             payment.action_post()

    def action_group_pay_now(self):
        for move in self:
            if move.move_type != 'out_invoice':
                continue  # only apply to customer invoices

            if move.state == 'draft':
                move.action_post()

            if move.payment_state != 'paid':
                # Get the manual payment method (cash)
                manual_payment_method = self.env.ref('account.account_payment_method_manual_in',
                                                     raise_if_not_found=False)
                if not manual_payment_method:
                    raise UserError(
                        "Manual Payment (Cash) method not found. Please configure it in Accounting settings.")

                payment_vals = {
                    'payment_type': 'inbound',  # for customer invoice
                    'partner_type': 'customer',
                    'partner_id': move.partner_id.id,
                    'amount': move.amount_residual,
                    'payment_method_line_id': manual_payment_method.id,
                    'journal_id': move.journal_id.id,
                    'payment_date': fields.Date.today(),
                    'ref': move.name,
                    'communication': move.name,
                    'currency_id': move.currency_id.id,
                    'destination_account_id':
                        move.line_ids.filtered(lambda l: l.account_id.user_type_id.type == 'receivable')[
                            0].account_id.id,
                }

                payment = self.env['account.payment'].create(payment_vals)
                payment.action_post()
                payment.move_id.line_ids.filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()





class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    department = fields.Selection([
        ('labour', 'Labour'),
        ('parts', 'Parts'),
        ('material', 'Material'),
        ('lubricant', 'Lubricant'),
        ('sublets', 'Sublets'),
        ('paint_material', 'Paint Material'),
        ('tyre', 'Tyre'),
        ('vehicle', 'Vehicle'),
    ], string="Department")




# this function is added for if the product is in vehicle then the account is in stock input
    @api.onchange('product_id')
    def _onchange_product_id_override_account(self):
        if self.product_id and self.move_id.move_type == 'in_invoice':
            if self.product_id.categ_id.name == 'Vehicles':
                input_account = self.product_id.categ_id.property_stock_valuation_account_id
                if input_account:
                    self.account_id = input_account.id


 # this function can be used if i select  department as vehicle
    # @api.onchange('product_id')
    # def _onchange_product_department_override_account(self):
    #     # Only for vendor bills
    #     if self.move_id.move_type == 'in_invoice' and self.product_id:
    #         # Check the department
    #         if getattr(self.product_id, 'department', False) == 'vehicle':
    #             input_account = self.product_id.categ_id.property_stock_valuation_account_id
    #             if input_account:
    #                 self.account_id = input_account.id