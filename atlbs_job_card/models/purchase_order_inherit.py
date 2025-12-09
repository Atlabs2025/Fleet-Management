from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


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



#################################remove this code before pushing################3
    is_storable = fields.Boolean(
        compute="_compute_is_storable",
        store=False
    )

    def _compute_is_storable(self):
        for rec in self:
            rec.is_storable = rec.product_id.type == 'product'


###########################################################################




    @api.depends("product_id")
    def _compute_stock_qty(self):
        for line in self:
            if line.product_id:
                # total on-hand quantity across all locations
                line.stock_qty = line.product_id.qty_available
            else:
                line.stock_qty = 0.0



# new change added the vehicle product should not be repeated



    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.vin_sn:
            # Check if VIN already used in the same purchase order
            duplicates = self.order_id.order_line.filtered(
                lambda l: l.product_id.vin_sn == self.product_id.vin_sn and l.id != self.id
            )
            if duplicates:
                raise UserError(
                    f"Vehicle with VIN '{self.product_id.vin_sn}' is already selected in this Purchase Order."
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


# added this create and write function for if we change the price from lines then it will be reflect in the inventory cost price also
#     @api.model
#     def create(self, vals):
#         line = super().create(vals)
#         if 'price_unit' in vals and line.product_id:
#             # Update product's standard price
#             line.product_id.sudo().write({'standard_price': line.price_unit})
#         return line
#
#     def write(self, vals):
#         res = super().write(vals)
#         if 'price_unit' in vals:
#             for line in self:
#                 if line.product_id:
#                     # Update product's standard price
#                     line.product_id.sudo().write({'standard_price': line.price_unit})
#         return res

    @api.model
    def create(self, vals):
        # Validate Vehicle quantity before creation
        product = self.env['product.product'].browse(vals.get('product_id'))
        if product and product.categ_id.name == "Vehicles" and vals.get('product_qty', 1) > 1:
            raise UserError(_("Quantity for Vehicle products cannot be greater than 1."))

        # Call super properly
        line = super(PurchaseOrderLine, self).create(vals)

        # Update standard price if provided
        if vals.get('price_unit') and line.product_id:
            line.product_id.sudo().write({'standard_price': line.price_unit})

        return line

    def write(self, vals):
        # Validate Vehicle quantity before writing
        if 'product_qty' in vals:
            for line in self:
                if line.product_id.categ_id.name == "Vehicles" and vals['product_qty'] > 1:
                    raise UserError(_("Quantity for Vehicle products cannot be greater than 1."))

        # Call super properly
        res = super(PurchaseOrderLine, self).write(vals)

        # Update standard price if provided
        if 'price_unit' in vals:
            for line in self:
                if line.product_id:
                    line.product_id.sudo().write({'standard_price': line.price_unit})

        return res


