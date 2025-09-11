from odoo import models, fields, api

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


    # def action_add_products(self):
    #
    #     self.ensure_one()
    #     purchase_order = self.purchase_order_id
    #
    #     for product in self.product_ids:
    #         # Build the description from vehicle fields
    #         description_text = ' '.join(filter(None, [
    #             product.vehicle_make_id if product.vehicle_make_id else '',
    #             product.model_id if product.model_id else '',
    #             product.colour_type or '',
    #         ]))
    #
    #         self.env['purchase.order.line'].create({
    #             'order_id': purchase_order.id,
    #             'product_id': product.id,
    #             'department': 'vehicle',
    #             'description': description_text,  # set description here
    #             'product_uom_qty': 1,  # default quantity
    #             'price_unit': product.list_price,
    #         })
    #
    #     return {'type': 'ir.actions.act_window_close'}

    def action_add_products(self):
        self.ensure_one()
        purchase_order = self.purchase_order_id

        for template in self.product_ids:  # these are product.template
            # Get the variant (always at least one)
            variant = template.product_variant_id

            # Build the description from vehicle fields (stored on template)
            description_text = ' '.join(filter(None, [
                template.vehicle_make_id if template.vehicle_make_id else '',
                template.vin_sn if template.vin_sn else '',
                template.model_id if template.model_id else '',
                template.colour_type or '',
            ]))

            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': variant.id,  # must be product.product
                'department': 'vehicle',
                'description': description_text,
                'product_uom_qty': 1,
                'price_unit': template.list_price,
            })

        return {'type': 'ir.actions.act_window_close'}

# class SaleOrderVehicleProductWizardLine(models.TransientModel):
#     _name = 'purchase.order.vehicle.product.wizard.line'
#     _description = 'Vehicle Product Line for Wizard'
#
#     wizard_id = fields.Many2one('purchase.order.vehicle.product.wizard', string="Wizard")
#     product_id = fields.Many2one(
#         'product.product',
#         string='Vehicle Product',
#         domain="[('categ_id.name', '=', 'Vehicles')]",
#     )
#     selected = fields.Boolean(string="Select")
#
#     year = fields.Char(string="Year")
#     model_id = fields.Char(string="Model")
#     vin_sn = fields.Char(string="Chassis Number")