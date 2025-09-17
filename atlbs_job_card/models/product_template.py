import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    menu_service = fields.Selection([
        ('regular', 'Regular'),
        ('medium', 'Medium'),
        ('major', 'Major'),
        ('loop_services', 'Loop Services'),
    ], string="Menu Services")

    service_amount = fields.Float(string="Service Amount")

    part_no = fields.Char(string="Part.No")

    @api.onchange('menu_service')
    def _onchange_menu_service(self):
        for rec in self:
            if rec.menu_service == 'regular':
                rec.service_amount = 500
            elif rec.menu_service == 'medium':
                rec.service_amount = 1000
            elif rec.menu_service == 'major':
                rec.service_amount = 2000
            elif rec.menu_service == 'loop_services':
                rec.service_amount = 300
            else:
                rec.service_amount = 0.0

    @api.onchange('part_no')
    def _onchange_part_no(self):
        if self.part_no != self.default_code:
            self.default_code = self.part_no



    @api.onchange('default_code')
    def _onchange_default_code(self):
        if self.default_code != self.part_no:
            self.part_no = self.default_code


# new function added for updating quantity
class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    def change_product_qty(self):
        for wizard in self:
            if wizard.product_id.categ_id.name == "Vehicles" and wizard.new_quantity != 1:
                raise UserError(_("Quantity for Vehicle products cannot be greater than 1."))

        return super(StockChangeProductQty, self).change_product_qty()