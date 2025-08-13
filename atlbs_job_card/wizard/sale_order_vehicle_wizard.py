from odoo import models, fields, api

class SaleOrderVehicleProductWizard(models.TransientModel):
    _name = 'sale.order.vehicle.product.wizard'
    _description = 'Select Vehicle Products to Add to Sale Order'

    product_ids = fields.Many2many(
        'product.product',
        domain="[('categ_id.name', '=', 'Vehicles')]",
        string='Vehicle Products'
    )
    sale_order_id = fields.Many2one('sale.order')

    def action_add_products(self):
        self.ensure_one()
        order_line_obj = self.env['sale.order.line']
        for product in self.product_ids:
            order_line_obj.create({
                'order_id': self.sale_order_id.id,
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': product.lst_price,
                'department': 'vehicle',  # Automatically set department as vehicle
            })
        return {'type': 'ir.actions.act_window_close'}

