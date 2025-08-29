from odoo import models, fields, api

class PurchaseOrderVehicleProductWizard(models.TransientModel):
    _name = 'purchase.order.vehicle.product.wizard'
    _description = 'Select Vehicle Products to Add to Purchase Order'

    # product_ids = fields.Many2many(
    #     'product.product',
    #     domain="[('categ_id.name', '=', 'Vehicles')]",
    #     string='Vehicle Products'
    # )

    purchase_order_id = fields.Many2one('purchase.order', string="Sale Order")
    line_ids = fields.One2many('purchase.order.vehicle.product.wizard.line', 'wizard_id', string="Products")

    # def action_add_products(self):
    #     self.ensure_one()
    #     order_line_obj = self.env['purchase.order.line']
    #     for product in self.product_ids:
    #         order_line_obj.create({
    #             'order_id': self.purchase_order_id.id,
    #             'product_id': product.id,
    #             'product_uom_qty': 1,
    #             'price_unit': product.lst_price,
    #             'department': 'vehicle',  # Automatically set department as vehicle
    #         })
    #     return {'type': 'ir.actions.act_window_close'}

    def action_add_products(self):
        self.ensure_one()
        order_line_obj = self.env['purchase.order.line']
        for line in self.line_ids.filtered('selected'):
            product = line.product_id
            description_text = ' '.join(filter(None, [
                getattr(product, 'vehicle_make_id', False) and product.vehicle_make_id,
                getattr(product, 'model_id', False) and product.model_id,
                getattr(product, 'colour_type', False) and product.colour_type,
            ]))
            order_line_obj.create({
                'order_id': self.purchase_order_id.id,
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': product.lst_price,
                'department': 'vehicle',
                'description': description_text,
            })
        return {'type': 'ir.actions.act_window_close'}





class SaleOrderVehicleProductWizardLine(models.TransientModel):
    _name = 'purchase.order.vehicle.product.wizard.line'
    _description = 'Vehicle Product Line for Wizard'

    wizard_id = fields.Many2one('purchase.order.vehicle.product.wizard', string="Wizard")
    product_id = fields.Many2one(
        'product.product',
        string='Vehicle Product',
        domain="[('categ_id.name', '=', 'Vehicles')]",
    )
    selected = fields.Boolean(string="Select")