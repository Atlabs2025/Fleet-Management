from odoo import models, fields, api



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'




    # def action_add_vehicle_products(self):
    #     all_vehicles = self.env['product.product'].search([('categ_id.name', '=', 'Vehicles')])
    #     wizard = self.env['purchase.order.vehicle.product.wizard'].create({'purchase_order_id': self.id})
    #     for product in all_vehicles:
    #         self.env['purchase.order.vehicle.product.wizard.line'].create({
    #             'wizard_id': wizard.id,
    #             'product_id': product.id,
    #             'year': product.year_of_manufacturing,
    #             'model_id': product.model_id,
    #             'vin_sn': product.vin_sn,
    #         })
    #     return {
    #         'name': 'Select Vehicle Products',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'purchase.order.vehicle.product.wizard',
    #         'view_mode': 'form',
    #         'res_id': wizard.id,
    #         'target': 'new',
    #     }
    #

    def action_open_vehicle_products(self):
        return {
            'name': 'Select Vehicle Products',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.vehicle.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_order_id': self.id
            }
        }





class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

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

    product_location_id = fields.Many2one(
            'stock.location',
            string="Product Location")

    stock_qty = fields.Float(
        string="Stock",
        compute="_compute_stock_qty",

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






# part number onchange
#     @api.onchange('product_template_id_next')
#     def _onchange_product_template_id_next(self):
#         for line in self:
#             if line.product_template_id_next:
#                 # Find first variant of this template
#                 variant = self.env['product.product'].search([('product_tmpl_id', '=', line.product_template_id_next.id)],
#                                                              limit=1)
#                 if variant:
#                     line.product_id = variant.id  # set product_id for normal onchange chain
#                     line.product_uom = variant.uom_id
#                     line.product_uom_qty = 1
#                 else:
#                     line.product_id = False
#                     line.product_uom = False

