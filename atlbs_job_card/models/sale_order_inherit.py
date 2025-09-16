from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    job_card_id = fields.Many2one("job.card.management", string="Job Card")



    def action_open_vehicle_products(self):
        """Open the wizard popup"""
        return {
            'name': 'Select Vehicle Products',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.vehicle.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id
            }
        }


    # def _create_invoices(self, **kwargs):
    #     invoices = super()._create_invoices(**kwargs)
    #     for order in self:
    #         if order.job_card_id:
    #             invoices.filtered(lambda inv: inv.invoice_origin == order.name).write({
    #                 "job_card_id": order.job_card_id.id
    #             })
    #     return invoices


# changed create invoice function becuase stock is not there it should not be invoiced
    def _create_invoices(self, **kwargs):
        for order in self:
            # Get stock location for the company
            stock_location = self.env['stock.location'].search([
                ('usage', '=', 'internal'),
                ('company_id', '=', order.company_id.id)
            ], limit=1)

            if not stock_location:
                raise UserError("No internal stock location found for the company's warehouse.")

            # Validate stock for all invoiceable products
            for line in order.order_line:
                if line.product_id.type in ['product', 'consu']:  # products that track stock
                    available_qty = self.env['stock.quant']._get_available_quantity(line.product_id, stock_location)
                    if available_qty <= 0:
                        raise UserError(
                            f"Cannot invoice '{line.product_id.name}' because there is no stock available in {stock_location.name}."
                        )

        # Call super to create invoices
        invoices = super()._create_invoices(**kwargs)

        # Link job_card_id if present
        for order in self:
            if order.job_card_id:
                invoices.filtered(lambda inv: inv.invoice_origin == order.name).write({
                    "job_card_id": order.job_card_id.id
                })

        return invoices




    def action_create_job_card(self):
        self.ensure_one()
        job_card = self.env['job.card.management'].create({
            'sale_order_id': self.id,
            'partner_id': self.partner_id.id,
            'email': self.partner_id.email,
            'phone': self.partner_id.phone,
            'whatsapp_no': self.partner_id.whatsapp_no,
            'state': 'memo',
        })
        # link back to sale order
        self.job_card_id = job_card.id

        job_card_line_obj = self.env['job.card.line']
        for line in self.order_line:
            job_card_line_obj.create({
                'job_card_id': job_card.id,
                'department': line.department,
                'product_template_id': line.product_template_id.id if hasattr(line, 'product_template_id') else False,
                'description': line.name,
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
                'tax_ids': [(6, 0, line.tax_id.ids)] if hasattr(line, 'tax_id') else False,
                'discount': line.discount,
                'after_discount': line.price_unit * (1 - (line.discount or 0.0) / 100),
                'uom': line.product_uom.id if hasattr(line, 'product_uom') else False,
            })
        return {
            'name': 'Job Card',
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.management',
            'view_mode': 'form',
            'res_id': job_card.id,
            'target': 'current',
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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
    # product_template_id_next = fields.Many2one('product.template', string="Part Number")

    stock_qty = fields.Float(
        string="Stock",
        compute="_compute_stock_qty",
        store=False
    )

    description = fields.Char(string='Description')

    @api.depends("product_id")
    def _compute_stock_qty(self):
        for line in self:
            if line.product_id:
                # total on-hand quantity across all locations
                line.stock_qty = line.product_id.qty_available
            else:
                line.stock_qty = 0.0


# added for vin number duplication prevention and create and write functions for feetching and reflecting the list price value into price unit and vise versa

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.vin_sn:
            # Check if VIN already used in the same sale order
            duplicates = self.order_id.order_line.filtered(
                lambda l: l.product_id.vin_sn == self.product_id.vin_sn and l.id != self.id
            )
            if duplicates:
                raise UserError(
                    f"Vehicle with VIN '{self.product_id.vin_sn}' is already selected in this Sale Order."
                )

        if self.order_id:
            # Build domain to hide already used VINs
            selected_vins = self.order_id.order_line.filtered(
                lambda l: l.product_id and l.product_id.vin_sn and l.id != self.id
            ).mapped('product_id.vin_sn')

            return {
                'domain': {
                    'product_id': [
                        '|',
                        ('vin_sn', '=', False),  # allow non-vehicle products
                        ('vin_sn', 'not in', selected_vins)
                    ]
                }
            }

    @api.model
    def create(self, vals):
        line = super().create(vals)
        if 'price_unit' in vals and line.product_id:
            # Update product's list price
            line.product_id.sudo().write({'list_price': line.price_unit})
        return line

    def write(self, vals):
        res = super().write(vals)
        if 'price_unit' in vals:
            for line in self:
                if line.product_id:
                    # Update product's list price
                    line.product_id.sudo().write({'list_price': line.price_unit})
        return res