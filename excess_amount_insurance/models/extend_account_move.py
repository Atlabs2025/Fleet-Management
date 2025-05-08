import datetime

from odoo import models, fields, api
from num2words import num2words


class AccountMove(models.Model):
    _inherit = "account.move"

    excess_amount_move_id = fields.Many2one("account.move", string="Invoice Excess Amount", copy=False)
    partner_excess_amount = fields.Many2one("res.partner", string="Charged To", copy=False)
    excess_amount = fields.Monetary(string="Excess Amount", copy=False)
    cc_total_amount = fields.Monetary(string="Total Amount", compute="depends_invoice_line_ids", store=True)
    payment_mode = fields.Selection([('cash', 'Cash'), ('card', 'Card')])

    @api.depends('invoice_line_ids')
    def depends_invoice_line_ids(self):
        for rec in self:
            invoice_line_ids = rec.invoice_line_ids
            rec.cc_total_amount = sum(invoice_line_ids.mapped('price_subtotal'))

    # @api.onchange('excess_amount')
    # def _add_excess_amount_line(self):
    #     if self.excess_amount:
    #         # Find or create the product for excess amount
    #         product_id = self.env['product.product'].search([
    #             ('name', '=', 'Excess Amount'),
    #             ('default_code', '=', 'PEA')
    #         ])
    #         if not product_id:
    #             product_id = self.env['product.product'].sudo().create({
    #                 'name': 'Excess Amount',
    #                 'default_code': 'PEA',
    #                 'type': 'service'
    #             })
    #
    #         # Add the new adjustment line
    #         self.invoice_line_ids = [(0, 0, {
    #             'product_id': product_id.id,
    #             'product_uom_id': product_id.uom_id.id,
    #             'tax_ids': product_id.taxes_id.ids if product_id.taxes_id else "",
    #             # 'account_id': product_id.property_account_income_id,
    #             'name': product_id.name,
    #             'quantity': 1,
    #             'currency_id': self.env.user.company_id.currency_id,
    #             'price_unit': -self.excess_amount,
    #         })]
    #         self._onchange_partner_id()
    #         # self.line_ids._onchange_account_id()
    #         # self.line_ids._onchange_price_subtotal()
    #         # self._recompute_dynamic_lines(
    #         #     recompute_all_taxes=True,
    #         #     recompute_tax_base_amount=True,
    #         # )
    #         self.cc_total_amount = sum(self.invoice_line_ids.mapped('price_subtotal'))

    @api.onchange('excess_amount')
    def _add_excess_amount_line(self):
        if self.excess_amount:
            # Find or create the product for excess amount
            product_id = self.env['product.product'].search([
                ('name', '=', 'Excess Amount'),
                ('default_code', '=', 'PEA')
            ], limit=1)
            if not product_id:
                product_id = self.env['product.product'].sudo().create({
                    'name': 'Excess Amount',
                    'default_code': 'PEA',
                    'type': 'service'
                })

            account = product_id._get_product_accounts()['income']

            # Remove existing excess amount lines
            new_lines = self.invoice_line_ids.filtered(lambda l: l.product_id != product_id)

            # Add the new excess amount line
            new_lines |= self.env['account.move.line'].new({
                'product_id': product_id.id,
                'product_uom_id': product_id.uom_id.id,
                'tax_ids': [(6, 0, product_id.taxes_id.ids)] if product_id.taxes_id else [],
                'account_id': account.id,
                'name': product_id.name,
                'quantity': 1,
                'currency_id': self.env.user.company_id.currency_id.id,
                'price_unit': -self.excess_amount,
            })

            self.invoice_line_ids = new_lines
            self._onchange_partner_id()
            self.cc_total_amount = sum(self.invoice_line_ids.mapped('price_subtotal'))

    def action_post(self):
        res = super(AccountMove, self).action_post()
        # if self.excess_amount and self.partner_excess_amount:
        #     excess_amount_move_id = self.excess_amount_move_id
        #     invoice = None
        #     product_id = self.env['product.product'].search([('name', '=', 'Excess Amount'), ('default_code', '=', 'PEA')])
        #     vals = [{
        #         'product_id': product_id.id,
        #         'tax_ids': product_id.taxes_id.ids if product_id.taxes_id else "",
        #         'name': product_id.name,
        #         'quantity': 1,
        #         'price_unit': self.excess_amount,
        #     }]
        #     if excess_amount_move_id:
        #         excess_amount_move_id.invoice_line_ids = [(5,0,0)]
        #         excess_amount_move_id.update({
        #             'partner_id': self.partner_excess_amount,
        #             'cc_vehicle': self.cc_vehicle.id if self.cc_vehicle else "",
        #         })
        #         excess_amount_move_id.action_post()
        #     else:
        #         invoice = self.create({
        #                             'partner_id': self.partner_excess_amount,
        #                             'invoice_date': datetime.date.today(),
        #                             'cc_vehicle': self.cc_vehicle.id if self.cc_vehicle else "",
        #                             'invoice_line_ids': vals
        #                         })
        #         invoice.action_post()
        #         self.excess_amount_move_id = invoice.id

        return res


    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        if self.excess_amount_move_id:
            self.excess_amount_move_id.button_draft()
            self.excess_amount_move_id.unlink()

        return res

    def num_convert_to_text(self, num):
        a = num2words(num)
        return a.upper()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_fixed = fields.Float(
        string="Excess Amount",
        digits="Product Price",
        default=0.00,
        help="Excess Amount",
    )
