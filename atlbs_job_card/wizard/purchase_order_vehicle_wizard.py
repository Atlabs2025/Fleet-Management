from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrderVehicleProductWizard(models.TransientModel):
    _name = 'purchase.order.vehicle.product.wizard'
    _description = 'Select Vehicle Products to Add to Purchase Order'

    # purchase_order_id = fields.Many2one('purchase.order', string="Sale Order")
    # line_ids = fields.One2many('purchase.order.vehicle.product.wizard.line', 'wizard_id', string="Products")

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    product_ids = fields.Many2many(
        'product.template',
        string="Products",
        domain=[('categ_id.name', '=', 'Vehicles')]
    )



# see this function changes because vin number validation and the cost price fetching into the unit price is done
    def action_add_products(self):
        self.ensure_one()
        purchase_order = self.purchase_order_id

        for template in self.product_ids:  # these are product.template
            variant = template.product_variant_id  # get product.product

            # Check if this VIN is already in the PO
            if variant.vin_sn:
                duplicates = purchase_order.order_line.filtered(
                    lambda l: l.product_id.vin_sn == variant.vin_sn
                )
                if duplicates:
                    raise UserError(
                        f"Vehicle with VIN '{variant.vin_sn}' is already selected in this Purchase Order."
                    )

            # Build the description from vehicle fields
            description_text = ' '.join(filter(None, [
                template.vehicle_make_id if template.vehicle_make_id else '',
                template.vin_sn if template.vin_sn else '',
                template.model_id if template.model_id else '',
                template.colour_type or '',
            ]))

            # Create purchase order line with cost price
            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': variant.id,
                'department': 'vehicle',
                'description': description_text,
                'product_uom_qty': 1,
                'price_unit': variant.standard_price,  # cost price
            })

        return {'type': 'ir.actions.act_window_close'}




    # def action_add_products(self):
    #     self.ensure_one()
    #     purchase_order = self.purchase_order_id
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
    #         self.env['purchase.order.line'].create({
    #             'order_id': purchase_order.id,
    #             'product_id': variant.id,  # must be product.product
    #             'department': 'vehicle',
    #             'description': description_text,
    #             'product_uom_qty': 1,
    #             'price_unit': template.list_price,
    #         })
    #
    #     return {'type': 'ir.actions.act_window_close'}
    #
