from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderVehicleProductWizard(models.TransientModel):
    _name = 'sale.order.vehicle.product.wizard'
    _description = 'Select Vehicle Products to Add to Sale Order'


    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    product_ids = fields.Many2many(
        'product.template',
        string="Products",
        domain=[('categ_id.name', '=', 'Vehicles')]
    )

    def action_add_products(self):
        self.ensure_one()
        sale_order = self.sale_order_id

        for template in self.product_ids:  # product.template
            # Get the variant (product.product)
            variant = template.product_variant_id

            # Check if VIN already exists in this sale order
            existing_lines = sale_order.order_line.filtered(
                lambda l: l.product_id.vin_sn == template.vin_sn
            )
            if existing_lines:
                raise UserError(f"Vehicle with VIN '{template.vin_sn}' is already added to this sale order.")

            # Build the description from vehicle fields
            description_text = ' '.join(filter(None, [
                template.vehicle_make_id if template.vehicle_make_id else '',
                template.vin_sn if template.vin_sn else '',
                template.model_id if template.model_id else '',
                template.colour_type or '',
            ]))

            # Create the sale order line
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': variant.id,
                'department': 'vehicle',
                'description': description_text,
                'product_uom_qty': 1,
                'price_unit': template.list_price,
            })

        return {'type': 'ir.actions.act_window_close'}


    # def action_add_products(self):
    #     self.ensure_one()
    #     sale_order = self.sale_order_id
    #
    #     for template in self.product_ids:  # these are product.template
    #         # Get the variant (always at least one)
    #         variant = template.product_variant_id
    #
    #         # Build the description from vehicle fields (stored on template)
    #         description_text = ' '.join(filter(None, [
    #             template.vehicle_make_id if template.vehicle_make_id else '',
    #             template.vin_sn if template.vin_sn else '',
    #             template.model_id if template.model_id else '',
    #             template.colour_type or '',
    #         ]))
    #
    #         self.env['sale.order.line'].create({
    #             'order_id': sale_order.id,
    #             'product_id': variant.id,  # must be product.product
    #             'department': 'vehicle',
    #             'description': description_text,
    #             'product_uom_qty': 1,
    #             'price_unit': template.list_price,
    #         })
    #
    #     return {'type': 'ir.actions.act_window_close'}


